-- SPDX-License-Identifier: Apache-2.0
-- Infinity AI - portao P3 (ADR-0136): a primeira escrita no jogo, por um gateway minimo.
--
-- O servico grava em override\INFAIACT.lua so a tabela INFAI_ACT_Request, com literais ja
-- validados: {action_id, op, area, name, cre, x, y, facing, count, strref}. Este modulo a rele a cada meio segundo
-- e, para um action_id novo:
--   SPAWN_CREATURE: o lider do grupo executa na hora a acao do proprio jogo, uma vez por copia
--     (count, ADR-0143), todas no mesmo instante,
--     CreateCreature("<CRE nosso>",[x.y],<direcao>), montada de um modelo fixo. No BG2:EE essa
--     acao nao recebe nome de script (ACTION.IDS): o nome nosso (INFAI_*) vem dentro do arquivo da
--     criatura, um dos nossos (IA*.CRE), instalado com o jogo fechado;
--   DESPAWN: acha na area a criatura com o nosso nome de script e executa nela, na hora, DestroySelf();
--   SET_HOSTILE (ADR-0142): executa Enemy() (acao do proprio jogo) nas criaturas vivas com o nosso
--     nome; depois de 3 s conta as vivas (before) e as hostis (observed, alianca >= 200).
--   CALL (ADR-0144): mostra sobre a cabeca de quem oferece a quest (criatura do jogo, pelo nome
--     de script) uma frase do dialog.tlk; so exibicao, responde na hora;
--   ESCAPE (ADR-0144): enfileira EscapeArea() nas nossas vivas com o nome; elas andam ate a saida
--     mais proxima e somem; conta a cada segundo, ate 30 s, ate nao sobrar nenhuma;
--   CHEGADA (ADR-0145): ao carregar uma area, cumpre o plano de chegada (INFAIARR.lua) dela: cria o
--     que falta de cada nome nosso no mesmo instante e responde cada entrada como um SPAWN;
--   PASSAGEM (ADR-0146): as passagens abertas pela quest (INFAIDOR.lua) para e de areas nossas;
--     o lider parado no ponto por 1 s leva o grupo (LeaveAreaLUA, um membro por vez, na hora);
--   WHERE (ADR-0146, laboratorio): so le onde o lider esta;
--   ANDAR (ADR-0148): um SPAWN (ou uma chegada) com to_x/to_y enfileira MoveToPoint() (acao do
--     proprio jogo, modelo fixo) nas nossas recem-criadas com o nome: nascem na porta e andam ate o
--     ponto, e ficam la;
--   CALL (ADR-0148): tambem sobre uma criatura nossa, quando a quest a declara;
--   REWARD (ADR-0148): o lider executa na hora GiveGoldForce() e AddexperienceParty() (modelo fixo,
--     valores da quest curada); depois de 1 s le o ouro do grupo: observed 1 se subiu exatamente o
--     valor (sem ouro, se o XP do lider subiu), senao UNVERIFIED (o servico nunca reenvia);
--   COUNT (ADR-0140): so le. Conta na area as criaturas VIVAS com o nosso nome e responde na hora,
--     sem executar nada. O seletor do jogo devolve tambem os corpos: o estado de morte (0x800,
--     a mesma checagem da caixa) os tira da conta, de COUNT, de SPAWN e de DESPAWN.
-- Responde no console (espelhado no InfinityLoader.log):
--   INFAI-ACT {"schema":"infinity-ai.act.v1","action_id":...,"status":"ACCEPTED|DONE|REFUSED",
--              "observed":N,"reason":...}
-- DONE traz quantas criaturas com o nosso nome a area tinha antes (before) e tem depois (observed),
-- e quantas criaturas a area tinha ao todo antes (seen_before) e depois (seen): as copias pedidas
-- nas duas contagens (ADR-0143), ou nenhuma, e a confirmacao do host. So arquivos IA* sao criados e so nomes INFAI_
-- sao removidos; nada do jogo original e tocado. O modulo
-- nunca atribui valores ao motor: so executa acoes do proprio jogo.
-- As tres acoes estao no INSTANT.IDS e rodam na hora (EEex ...Instantly), sem passar pela fila de
-- quem age: no laboratorio (ADR-0142), um CreateCreature na fila do lider se perdeu quando o
-- primeiro inimigo nascido hostil pausou o jogo e o grupo entrou em combate.

INFAI_ACT_SCHEMA = "infinity-ai.act.v1"
INFAI_ACT_POLL_MS = 500
INFAI_ACT_CHECK_MS = 3000        -- espera antes de contar o resultado
INFAI_ACT_RANGE = 30000          -- a area inteira; o motor usa raio de 16 bits com sinal (65535 vira -1)
INFAI_ACT_STATE_DEAD = 0x800     -- STATE.IDS: o seletor do jogo devolve tambem os corpos (lab, ADR-0140)
INFAI_ACT_EVILCUTOFF = 200       -- EA.IDS: de 200 para cima e inimigo do grupo (ADR-0142)
INFAI_ACT_MAX_COUNT = 8          -- ADR-0143: copias criadas juntas num pedido
INFAI_ACT_COPY_STEP = 40         -- ADR-0143: pixels entre uma copia e a seguinte
INFAI_ACT_ESCAPE_MS = 30000      -- ADR-0144: quanto a saida pela porta pode levar
INFAI_ACT_ESCAPE_STEP_MS = 1000  -- ADR-0144: de quanto em quanto se conta durante a saida
INFAI_ARR_SETTLE_MS = 300        -- ADR-0145: espera minima depois da troca de area
INFAI_DOOR_RADIUS = 60           -- ADR-0146: px em volta do ponto da passagem
INFAI_DOOR_STILL_MS = 1000       -- ADR-0146: quanto o lider fica no ponto antes de passar
INFAI_DOOR_RELOAD_MS = 5000      -- ADR-0146: rele o plano de passagens com o grupo na area
INFAI_ACT_REWARD_MS = 1000       -- ADR-0148: espera antes de conferir o ouro
INFAI_ACT_MAX_GOLD = 10000       -- ADR-0148: os limites da recompensa de uma quest
INFAI_ACT_MAX_XP = 50000

INFAI_ACT_State = INFAI_ACT_State or { done = {}, check = nil, next_poll = 0, arrivals = {},
	arr_area = nil }

local function infai_json_string(s)
	s = string.gsub(s, '[%c"\\]', function(c)
		if c == '"' then return '\\"' end
		if c == '\\' then return '\\\\' end
		return string.format('\\u%04x', string.byte(c))
	end)
	return '"' .. s .. '"'
end

local function infai_act_emit(id, status, observed, reason, before, seen, seen_before, px, py)
	print("INFAI-ACT {" ..
		'"schema":' .. infai_json_string(INFAI_ACT_SCHEMA) ..
		',"action_id":' .. infai_json_string(id) ..
		',"status":' .. infai_json_string(status) ..
		',"observed":' .. (type(observed) == "number" and string.format("%d", observed) or "null") ..
		',"reason":' .. (reason and infai_json_string(reason) or "null") ..
		',"before":' .. (type(before) == "number" and string.format("%d", before) or "null") ..
		',"seen":' .. (type(seen) == "number" and string.format("%d", seen) or "null") ..
		',"seen_before":' .. (type(seen_before) == "number" and string.format("%d", seen_before) or "null") ..
		(type(px) == "number" and string.format(',"x":%d,"y":%d', px, py) or "") .. '}')
end

-- So o arquivo de pedido do servico e descartado do cache (como INFAIRSP na caixa).
local function infai_act_drop_cached(resref)
	return pcall(function()
		local res = EEex_Resource_Fetch(resref or "INFAIACT", "LUA")
		if res ~= nil then EngineGlobals.dimmDump(res) end
	end)
end

local function infai_act_op_ok(op)
	return op == "SPAWN_CREATURE" or op == "DESPAWN" or op == "COUNT" or op == "SET_HOSTILE"
		or op == "CALL" or op == "ESCAPE" or op == "WHERE" or op == "REWARD"
end

local function infai_act_int(v, lo, hi)
	return type(v) == "number" and v == math.floor(v) and v >= lo and v <= hi
end

local function infai_act_valid(req)
	if type(req) ~= "table" or type(req.action_id) ~= "string" then return false end
	if not string.match(req.action_id, "^[a-z0-9]+$") or #req.action_id ~= 10 then return false end
	if not infai_act_op_ok(req.op) then return false end
	if type(req.area) ~= "string" or not string.match(req.area, "^[A-Z0-9]+$") or #req.area > 8 then
		return false
	end
	if type(req.name) ~= "string" or #req.name > 32 then return false end
	if req.op == "CALL" then
		-- ADR-0144: o nome de script de quem oferece a quest e uma frase do dialog.tlk; so
		-- exibicao. ADR-0148: pode ser uma criatura nossa, quando a quest a declara.
		if not string.match(req.name, "^[A-Z0-9_]+$") then
			return false
		end
		local r = req.strref
		if type(r) ~= "number" or r ~= math.floor(r) or r < 0 or r > 999999 then return false end
		return true
	end
	-- O nome e sempre nosso: INFAI_ e letras, numeros ou sublinhado, ate 32 caracteres.
	if not string.match(req.name, "^INFAI_[A-Z0-9_]+$") then
		return false
	end
	if req.op == "REWARD" then
		-- ADR-0148: so ouro e XP dentro dos limites, ao menos um; nenhuma criatura e nomeada.
		if req.name ~= "INFAI_PARTY" or not infai_act_int(req.gold, 0, INFAI_ACT_MAX_GOLD)
				or not infai_act_int(req.xp, 0, INFAI_ACT_MAX_XP) or req.gold + req.xp == 0 then
			return false
		end
		return req.count == nil or req.count == 1
	elseif (req.gold ~= nil and req.gold ~= 0) or (req.xp ~= nil and req.xp ~= 0) then
		return false
	end
	local tx, ty = req.to_x, req.to_y
	if tx ~= nil or ty ~= nil then
		-- ADR-0148: o ponto ate onde andar, os dois ou nenhum, so num SPAWN com ponto de nascer
		if not infai_act_int(tx, -1, 32767) or not infai_act_int(ty, -1, 32767)
				or (tx < 0) ~= (ty < 0) then
			return false
		end
		if tx >= 0 and (req.op ~= "SPAWN_CREATURE" or type(req.x) ~= "number" or req.x < 0) then
			return false
		end
	end
	if req.op == "SPAWN_CREATURE" then
		-- So os nossos arquivos de criatura (IA*), que trazem o nome nosso dentro.
		if type(req.cre) ~= "string" or not string.match(req.cre, "^IA[A-Z0-9]+$") or #req.cre > 8 then
			return false
		end
		for _, v in ipairs({ req.x, req.y }) do
			if type(v) ~= "number" or v ~= math.floor(v) or v < -1 or v > 32767 then return false end
		end
		if type(req.facing) ~= "number" or req.facing < 0 or req.facing > 15 then return false end
		-- ADR-0143: as copias nascem juntas, de 1 a 8 (o limite de copies de uma presenca)
		local n = req.count
		if type(n) ~= "number" or n ~= math.floor(n) or n < 1 or n > INFAI_ACT_MAX_COUNT then return false end
	elseif req.count ~= nil and req.count ~= 1 then
		return false
	end
	return true
end

local function infai_act_area()
	local ok, area = pcall(EEex_Area_GetVisible)
	if ok then return area end
	return nil
end

local function infai_act_area_name(area)
	local ok, name = pcall(function() return area.m_resref:get() end)
	if ok then return name end
	return nil
end

-- Morta pelo estado do proprio jogo (bit 0x800), como a caixa faz; sem leitura, conta como viva.
local function infai_act_dead(sprite)
	local ok, state = pcall(function() return sprite.m_baseStats.m_generalState end)
	if not ok or type(state) ~= "number" then return false end
	return math.floor(state / INFAI_ACT_STATE_DEAD) % 2 == 1
end

-- Hostil pela alianca do proprio jogo (EA.IDS); sem leitura, nao conta como hostil.
local function infai_act_hostile(sprite)
	local ok, ea = pcall(function() return sprite.m_typeAI.m_EnemyAlly end)
	return ok and type(ea) == "number" and ea >= INFAI_ACT_EVILCUTOFF
end

-- As criaturas VIVAS da area com este nome de script (comparacao sem caixa), e quantas a busca viu
-- ao todo (diagnostico: zero visto quer dizer busca quebrada, nao criatura ausente).
local function infai_act_find(area, name)
	local found, seen = {}, 0
	pcall(function()
		-- Sem linha de visao: o EEex faz "bCheckForLineOfSight or 1", entao false LIGA a checagem
		-- (do canto 0,0 ninguem esta a vista; laboratorio, S1x). Zero e verdadeiro em Lua e a desliga.
		local all = EEex_Area_GetAllOfTypeStringInRange(area, 0, 0, "[ANYONE]", INFAI_ACT_RANGE, 0, 0)
		seen = #all
		for _, sprite in ipairs(all) do
			local okn, script = pcall(function() return sprite.m_scriptName:get() end)
			if okn and type(script) == "string" and string.upper(script) == string.upper(name)
					and not infai_act_dead(sprite) then
				table.insert(found, sprite)
			end
		end
	end)
	return found, seen
end

-- O lider executa na hora CreateCreature uma vez por copia, um passo ao lado a cada uma (ADR-0143).
-- Devolve nil se deu certo, ou o motivo da recusa.
local function infai_act_create(cre, x, y, facing, n)
	local okl, leader = pcall(EEex_Sprite_GetInPortrait, 0)
	if not okl or leader == nil then return "NO_PARTY" end
	if x < 0 then
		local okp = pcall(function() x, y = leader.m_pos.x + 60, leader.m_pos.y + 30 end)
		if not okp then return "NO_POINT" end
	end
	for i = 0, n - 1 do
		local xi = math.min(x + INFAI_ACT_COPY_STEP * i, 32767)
		local action = string.format('CreateCreature("%s",[%d.%d],%d)', cre, xi, y, facing)
		local okq = pcall(EEex_Action_ExecuteResponseStringOnAIBaseInstantly, action, leader)
		if not okq then return "ACTION_FAILED" end
	end
	return nil
end

-- ADR-0148: as nossas com o nome andam ate o ponto (MoveToPoint, modelo fixo, na fila delas).
local function infai_act_walk(area, name, tx, ty)
	if type(tx) ~= "number" or tx < 0 then return end
	local action = string.format('MoveToPoint([%d.%d])', tx, ty)
	for _, sprite in ipairs(infai_act_find(area, name)) do
		pcall(EEex_Action_QueueResponseStringOnAIBase, action, sprite)
	end
end

-- ADR-0148: o ouro do grupo e o XP do lider, so leitura; nil sem leitura. Varios caminhos, o
-- primeiro que der um numero vale (laboratorio 2026-11-26: m_nPartyGold nao leu; a interface do
-- proprio jogo usa game:GetPartyGold()). Um Primitive<> do EEex traz o numero em m_value.
local function infai_act_num(get)
	local ok, v = pcall(get)
	if not ok then return nil end
	if type(v) == "number" then return v end
	if v ~= nil then
		local okv, inner = pcall(function() return v.m_value end)
		if okv and type(inner) == "number" then return inner end
	end
	return nil
end

local INFAI_ACT_GOLD_READS = {
	function() return game:GetPartyGold() end,
	function() return EEex_EngineGlobal_CBaldurChitin.m_pObjectGame.m_nPartyGold end,
	function() return EngineGlobals.g_pBaldurChitin.m_pObjectGame.m_nPartyGold end,
}

local INFAI_ACT_XP_READS = {
	function() return EEex_Sprite_GetActiveStats(EEex_Sprite_GetInPortrait(0)).m_nXP end,
	function() return EEex_Sprite_GetInPortrait(0).m_baseStats.m_xp end,
}

local function infai_act_first(reads)
	for i = 1, #reads do
		local v = infai_act_num(reads[i])
		if v ~= nil then return v, i end
	end
	return nil, nil
end

local function infai_act_gold() return infai_act_first(INFAI_ACT_GOLD_READS) end
local function infai_act_xp() return infai_act_first(INFAI_ACT_XP_READS) end

-- O lider do grupo ja esta nesta area (o motor o poe depois de trocar a area visivel).
local function infai_act_leader_in(area)
	local ok, same = pcall(function()
		local leader = EEex_Sprite_GetInPortrait(0)
		return leader ~= nil and EEex_UDEqual(leader.m_pArea, area)
	end)
	return ok and same == true
end

-- ADR-0146: as passagens que a quest abriu (INFAIDOR) nesta area: o lider parado no ponto, por
-- um segundo, leva o grupo pela acao do proprio jogo de trocar de area. So de/para areas nossas
-- (IA e quatro digitos), nunca com inimigo vivo na area, e so depois de o lider sair do ponto uma
-- vez (para nao voltar ao chegar).
local function infai_door_ok(e, name)
	if type(e) ~= "table" or type(e.id) ~= "string" or not string.match(e.id, "^[a-z0-9]+$")
			or #e.id ~= 10 or e.area ~= name or type(e.to) ~= "string"
			or not string.match(e.to, "^[A-Z0-9]+$") or #e.to > 8 or e.to == e.area then
		return false
	end
	if not string.match(e.area, "^IA%d%d%d%d$") and not string.match(e.to, "^IA%d%d%d%d$") then
		return false
	end
	for _, v in ipairs({ e.x, e.y, e.to_x, e.to_y }) do
		if type(v) ~= "number" or v ~= math.floor(v) or v < 0 or v > 32767 then return false end
	end
	return type(e.facing) == "number" and e.facing >= 0 and e.facing <= 15
end

local function infai_door_load(name)
	local st = INFAI_ACT_State
	st.doors = {}
	INFAI_DOOR_Plan = nil
	infai_act_drop_cached("INFAIDOR")
	pcall(Infinity_DoFile, "INFAIDOR")
	if type(INFAI_DOOR_Plan) ~= "table" then return end
	for _, e in ipairs(INFAI_DOOR_Plan) do
		if infai_door_ok(e, name) then
			table.insert(st.doors, { e = e, armed = false, since = nil })
		end
	end
end

local function infai_door_enemy(area)
	local ok, any = pcall(function()
		local all = EEex_Area_GetAllOfTypeStringInRange(area, 0, 0, "[ANYONE]", INFAI_ACT_RANGE, 0, 0)
		for _, sprite in ipairs(all) do
			if infai_act_hostile(sprite) and not infai_act_dead(sprite) then return true end
		end
		return false
	end)
	return not ok or any
end

local function infai_door_tick(area, now)
	local st = INFAI_ACT_State
	if st.doors == nil or #st.doors == 0 then return end
	local ok, lx, ly = pcall(function()
		local leader = EEex_Sprite_GetInPortrait(0)
		return leader.m_pos.x, leader.m_pos.y
	end)
	if not ok or type(lx) ~= "number" then return end
	for _, d in ipairs(st.doors) do
		local dx, dy = lx - d.e.x, ly - d.e.y
		local inside = dx * dx + dy * dy <= INFAI_DOOR_RADIUS * INFAI_DOOR_RADIUS
		if not inside then
			d.armed, d.since = true, nil
		elseif d.armed then
			d.since = d.since or now
			if now >= d.since + INFAI_DOOR_STILL_MS and not infai_door_enemy(area) then
				d.armed, d.since = false, nil
				local action = string.format('LeaveAreaLUA("%s","",[%d.%d],%d)', d.e.to, d.e.to_x,
					d.e.to_y, d.e.facing)
				local moved = 0
				for i = 0, 5 do
					local okm, member = pcall(EEex_Sprite_GetInPortrait, i)
					if okm and member ~= nil then
						if pcall(EEex_Action_ExecuteResponseStringOnAIBaseInstantly, action, member) then
							moved = moved + 1
						end
					end
				end
				infai_act_emit(d.e.id, "DONE", moved, nil, 0)
				return
			end
		end
	end
end

-- ADR-0145: ao carregar uma area do plano de chegada (INFAIARR), conta e cria no mesmo instante o
-- que falta de cada nome, antes de o grupo dar o primeiro passo; cada entrada responde como um
-- SPAWN (antes, depois e o total da area), depois da mesma espera.
local function infai_arr_enter(area, name, now)
	local st = INFAI_ACT_State
	INFAI_ARR_Plan = nil
	infai_act_drop_cached("INFAIARR")
	pcall(Infinity_DoFile, "INFAIARR")
	local plan = INFAI_ARR_Plan
	if type(plan) ~= "table" then return end
	for _, e in ipairs(plan) do
		local req = type(e) == "table" and { action_id = e.action_id, op = "SPAWN_CREATURE",
			area = e.area, name = e.name, cre = e.cre, x = e.x, y = e.y, facing = e.facing,
			count = e.count, to_x = e.to_x, to_y = e.to_y } or nil
		if req ~= nil and req.area == name and type(req.action_id) == "string"
				and not st.done[req.action_id] and infai_act_valid(req) then
			st.done[req.action_id] = true
			local found, seen_before = infai_act_find(area, req.name)
			local missing = req.count - #found
			local refused = nil
			if missing > 0 then
				refused = infai_act_create(req.cre, req.x, req.y, req.facing, missing)
				if refused == nil then infai_act_walk(area, req.name, req.to_x, req.to_y) end
			end
			if refused ~= nil then
				infai_act_emit(req.action_id, "REFUSED", nil, refused)
			else
				table.insert(st.arrivals, { id = req.action_id, name = req.name, before = #found,
					seen_before = seen_before, at = now + INFAI_ACT_CHECK_MS })
			end
		end
	end
end

local function infai_act_run(req, now)
	local st = INFAI_ACT_State
	local area = infai_act_area()
	if area == nil or infai_act_area_name(area) ~= req.area then
		infai_act_emit(req.action_id, "REFUSED", nil, "WRONG_AREA")
		return
	end
	if req.op == "COUNT" then
		local found, seen = infai_act_find(area, req.name)
		infai_act_emit(req.action_id, "DONE", #found, nil, #found, seen)
		return
	end
	if req.op == "WHERE" then
		-- ADR-0146 (laboratorio): onde o lider esta, so leitura, para marcar o ponto de uma passagem
		local ok, x, y = pcall(function()
			local leader = EEex_Sprite_GetInPortrait(0)
			return leader.m_pos.x, leader.m_pos.y
		end)
		if ok and type(x) == "number" then
			infai_act_emit(req.action_id, "DONE", 1, nil, 1, nil, nil, x, y)
		else
			infai_act_emit(req.action_id, "REFUSED", nil, "NO_PARTY")
		end
		return
	end
	if req.op == "REWARD" then
		-- ADR-0148: paga na hora, pelo lider, com as acoes do proprio jogo; confere o ouro depois.
		local okl, leader = pcall(EEex_Sprite_GetInPortrait, 0)
		if not okl or leader == nil then
			infai_act_emit(req.action_id, "REFUSED", nil, "NO_PARTY")
			return
		end
		local gold_before, gold_how = infai_act_gold()
		local xp_before, xp_how = infai_act_xp()
		-- laboratorio: qual caminho leu o ouro e o XP (nenhum dado do jogador, so numeros)
		print(string.format("INFAI-DIAG reward gold=%s via=%s xp=%s via=%s", tostring(gold_before),
			tostring(gold_how), tostring(xp_before), tostring(xp_how)))
		if req.gold > 0 then
			pcall(EEex_Action_ExecuteResponseStringOnAIBaseInstantly,
				string.format('GiveGoldForce(%d)', req.gold), leader)
		end
		if req.xp > 0 then
			pcall(EEex_Action_ExecuteResponseStringOnAIBaseInstantly,
				string.format('AddexperienceParty(%d)', req.xp), leader)
		end
		infai_act_emit(req.action_id, "ACCEPTED", nil, nil)
		st.check = { id = req.action_id, op = "REWARD", gold = req.gold, xp = req.xp,
			gold_before = gold_before, xp_before = xp_before, at = now + INFAI_ACT_REWARD_MS }
		return
	end
	if req.op == "CALL" then
		-- ADR-0144: a frase sobre a cabeca, pela mensagem que o jogo usa nas falas de ambiente;
		-- nada muda no jogo nem no save.
		local targets = infai_act_find(area, req.name)
		if #targets == 0 then
			infai_act_emit(req.action_id, "REFUSED", 0, "NOT_FOUND")
			return
		end
		for _, sprite in ipairs(targets) do
			pcall(EEex_Sprite_DisplayTextRef, sprite, req.strref, { overHead = true })
		end
		infai_act_emit(req.action_id, "DONE", #targets, nil, #targets)
		return
	end
	if req.op == "ESCAPE" then
		-- ADR-0144: EscapeArea() anda ate a saida mais proxima e some la; nao e instantanea (a
		-- criatura anda), entao vai na fila dela, nossa e fora de combate. A conta espera ate 30 s.
		local targets, seen_before = infai_act_find(area, req.name)
		if #targets == 0 then
			infai_act_emit(req.action_id, "REFUSED", 0, "NOT_FOUND")
			return
		end
		for _, sprite in ipairs(targets) do
			pcall(EEex_Action_QueueResponseStringOnAIBase, "EscapeArea()", sprite)
		end
		infai_act_emit(req.action_id, "ACCEPTED", nil, nil)
		INFAI_ACT_State.check = { id = req.action_id, name = req.name, before = #targets,
			seen_before = seen_before, at = now + INFAI_ACT_ESCAPE_STEP_MS,
			deadline = now + INFAI_ACT_ESCAPE_MS, op = "ESCAPE" }
		return
	end
	if req.op == "SET_HOSTILE" then
		local targets = infai_act_find(area, req.name)
		if #targets == 0 then
			infai_act_emit(req.action_id, "REFUSED", 0, "NOT_FOUND")
			return
		end
		for _, sprite in ipairs(targets) do
			pcall(EEex_Action_ExecuteResponseStringOnAIBaseInstantly, "Enemy()", sprite)
		end
		infai_act_emit(req.action_id, "ACCEPTED", nil, nil)
		INFAI_ACT_State.check = { id = req.action_id, name = req.name, before = #targets,
			at = now + INFAI_ACT_CHECK_MS, op = "SET_HOSTILE" }
		return
	end
	local found_before, seen_before = infai_act_find(area, req.name)
	local before = #found_before
	if req.op == "SPAWN_CREATURE" then
		-- ADR-0143: todas as copias no mesmo instante, antes que uma luta comece.
		local refused = infai_act_create(req.cre, req.x, req.y, req.facing, req.count)
		if refused ~= nil then
			infai_act_emit(req.action_id, "REFUSED", nil, refused)
			return
		end
		infai_act_walk(area, req.name, req.to_x, req.to_y)
	else
		local targets = infai_act_find(area, req.name)
		if #targets == 0 then
			infai_act_emit(req.action_id, "REFUSED", 0, "NOT_FOUND")
			return
		end
		for _, sprite in ipairs(targets) do
			pcall(EEex_Action_ExecuteResponseStringOnAIBaseInstantly, "DestroySelf()", sprite)
		end
	end
	infai_act_emit(req.action_id, "ACCEPTED", nil, nil)
	st.check = { id = req.action_id, name = req.name, before = before, seen_before = seen_before,
		at = now + INFAI_ACT_CHECK_MS }
end

-- Chamado a cada frame pelo menu oculto INFAI_ACT_Menu (INFAIAM.menu). Retorna false.
function INFAI_ACT_Tick()
	local st = INFAI_ACT_State
	local now = Infinity_GetClockTicks()
	-- ADR-0145: a area carregada mudou? Cumpre o plano de chegada dela, uma vez, quando o lider
	-- ja esta nela (lab: na troca de area, o grupo ainda nao foi posto, e criar falha calado).
	local here = infai_act_area()
	local here_name = here ~= nil and infai_act_area_name(here) or nil
	if here_name ~= st.arr_area then
		st.arr_area = here_name
		st.arr_wait = here_name ~= nil and { name = here_name, since = now } or nil
	end
	if st.arr_wait ~= nil and here_name == st.arr_wait.name
			and now >= st.arr_wait.since + INFAI_ARR_SETTLE_MS and infai_act_leader_in(here) then
		st.arr_wait = nil
		infai_arr_enter(here, here_name, now)
		infai_door_load(here_name)
	end
	if st.arr_wait == nil and here ~= nil then
		if now >= (st.door_next or 0) then          -- a passage opened while the party is here
			st.door_next = now + INFAI_DOOR_RELOAD_MS
			local keep = {}
			for _, d in ipairs(st.doors or {}) do keep[d.e.id] = d end
			infai_door_load(here_name)
			for _, d in ipairs(st.doors) do         -- keep each passage's state across reloads
				if keep[d.e.id] ~= nil then d.armed, d.since = keep[d.e.id].armed, keep[d.e.id].since end
			end
		end
		infai_door_tick(here, now)
	end
	local waiting = {}
	for _, a in ipairs(st.arrivals) do
		if now >= a.at and here ~= nil then
			local found, seen = infai_act_find(here, a.name)
			infai_act_emit(a.id, "DONE", #found, nil, a.before, seen, a.seen_before)
		else
			table.insert(waiting, a)
		end
	end
	st.arrivals = waiting
	if st.check ~= nil and now >= st.check.at and st.check.op == "REWARD" then
		local c = st.check
		local gold_after = infai_act_gold()
		local xp_after = infai_act_xp()
		print(string.format("INFAI-DIAG reward-after gold=%s xp=%s", tostring(gold_after), tostring(xp_after)))
		local paid
		if c.gold > 0 then
			paid = c.gold_before ~= nil and gold_after ~= nil and gold_after - c.gold_before == c.gold
		else
			paid = c.xp_before ~= nil and xp_after ~= nil and xp_after > c.xp_before
		end
		if paid then
			infai_act_emit(c.id, "DONE", 1, nil)
		else
			infai_act_emit(c.id, "DONE", nil, "UNVERIFIED")
		end
		st.check = nil
	end
	if st.check ~= nil and now >= st.check.at then
		local area = infai_act_area()
		local count, seen, before = nil, nil, st.check.before
		if area ~= nil then
			local found
			found, seen = infai_act_find(area, st.check.name)
			count = #found
			if st.check.op == "ESCAPE" and count > 0 and now < st.check.deadline then
				st.check.at = now + INFAI_ACT_ESCAPE_STEP_MS   -- ainda andando ate a saida
				return false
			end
			if st.check.op == "SET_HOSTILE" then        -- vivas (before) e hostis (observed)
				before = #found
				count = 0
				for _, sprite in ipairs(found) do
					if infai_act_hostile(sprite) then count = count + 1 end
				end
			end
		end
		infai_act_emit(st.check.id, "DONE", count, nil, before, seen, st.check.seen_before)
		st.check = nil
	end
	if now < st.next_poll or st.check ~= nil then return false end
	st.next_poll = now + INFAI_ACT_POLL_MS
	INFAI_ACT_Request = nil
	infai_act_drop_cached()
	pcall(Infinity_DoFile, "INFAIACT")
	local req = INFAI_ACT_Request
	if type(req) ~= "table" or req.action_id == "" or req.action_id == nil then return false end
	if st.done[req.action_id] then return false end
	st.done[req.action_id] = true
	if not infai_act_valid(req) then
		infai_act_emit(type(req.action_id) == "string" and req.action_id or "", "REFUSED", nil, "BAD_REQUEST")
		return false
	end
	infai_act_run(req, now)
	return false
end

EEex_Menu_AddMainFileLoadedListener(function()
	EEex_Menu_LoadFile("INFAIAM")
end)

local function infai_act_push_menu()
	Infinity_PushMenu("INFAI_ACT_Menu")
end
EEex_GameState_AddInitializedListener(infai_act_push_menu)
EEex_Menu_AddAfterMainFileReloadedListener(infai_act_push_menu)

print("INFAI-ACT-DEBUG modulo carregado")
