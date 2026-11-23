-- SPDX-License-Identifier: Apache-2.0
-- Infinity AI - portao P3 (ADR-0136): a primeira escrita no jogo, por um gateway minimo.
--
-- O servico grava em override\INFAIACT.lua so a tabela INFAI_ACT_Request, com literais ja
-- validados: {action_id, op, area, name, cre, x, y, facing}. Este modulo a rele a cada meio segundo
-- e, para um action_id novo:
--   SPAWN_CREATURE: o lider do grupo executa na hora a acao do proprio jogo
--     CreateCreature("<CRE nosso>",[x.y],<direcao>), montada de um modelo fixo. No BG2:EE essa
--     acao nao recebe nome de script (ACTION.IDS): o nome nosso (INFAI_*) vem dentro do arquivo da
--     criatura, um dos nossos (IA*.CRE), instalado com o jogo fechado;
--   DESPAWN: acha na area a criatura com o nosso nome de script e executa nela, na hora, DestroySelf();
--   SET_HOSTILE (ADR-0142): executa Enemy() (acao do proprio jogo) nas criaturas vivas com o nosso
--     nome; depois de 3 s conta as vivas (before) e as hostis (observed, alianca >= 200).
--   COUNT (ADR-0140): so le. Conta na area as criaturas VIVAS com o nosso nome e responde na hora,
--     sem executar nada. O seletor do jogo devolve tambem os corpos: o estado de morte (0x800,
--     a mesma checagem da caixa) os tira da conta, de COUNT, de SPAWN e de DESPAWN.
-- Responde no console (espelhado no InfinityLoader.log):
--   INFAI-ACT {"schema":"infinity-ai.act.v1","action_id":...,"status":"ACCEPTED|DONE|REFUSED",
--              "observed":N,"reason":...}
-- DONE traz quantas criaturas com o nosso nome a area tinha antes (before) e tem depois (observed):
-- uma a mais, ou nenhuma, e a confirmacao do host. So arquivos IA* sao criados e so nomes INFAI_
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

INFAI_ACT_State = INFAI_ACT_State or { done = {}, check = nil, next_poll = 0 }

local function infai_json_string(s)
	s = string.gsub(s, '[%c"\\]', function(c)
		if c == '"' then return '\\"' end
		if c == '\\' then return '\\\\' end
		return string.format('\\u%04x', string.byte(c))
	end)
	return '"' .. s .. '"'
end

local function infai_act_emit(id, status, observed, reason, before, seen)
	print("INFAI-ACT {" ..
		'"schema":' .. infai_json_string(INFAI_ACT_SCHEMA) ..
		',"action_id":' .. infai_json_string(id) ..
		',"status":' .. infai_json_string(status) ..
		',"observed":' .. (type(observed) == "number" and string.format("%d", observed) or "null") ..
		',"reason":' .. (reason and infai_json_string(reason) or "null") ..
		',"before":' .. (type(before) == "number" and string.format("%d", before) or "null") ..
		',"seen":' .. (type(seen) == "number" and string.format("%d", seen) or "null") .. '}')
end

-- So o arquivo de pedido do servico e descartado do cache (como INFAIRSP na caixa).
local function infai_act_drop_cached()
	return pcall(function()
		local res = EEex_Resource_Fetch("INFAIACT", "LUA")
		if res ~= nil then EngineGlobals.dimmDump(res) end
	end)
end

local function infai_act_op_ok(op)
	return op == "SPAWN_CREATURE" or op == "DESPAWN" or op == "COUNT" or op == "SET_HOSTILE"
end

local function infai_act_valid(req)
	if type(req) ~= "table" or type(req.action_id) ~= "string" then return false end
	if not string.match(req.action_id, "^[a-z0-9]+$") or #req.action_id ~= 10 then return false end
	if not infai_act_op_ok(req.op) then return false end
	if type(req.area) ~= "string" or not string.match(req.area, "^[A-Z0-9]+$") or #req.area > 8 then
		return false
	end
	-- O nome e sempre nosso: INFAI_ e letras, numeros ou sublinhado, ate 32 caracteres.
	if type(req.name) ~= "string" or #req.name > 32 or not string.match(req.name, "^INFAI_[A-Z0-9_]+$") then
		return false
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
	local before = #infai_act_find(area, req.name)
	if req.op == "SPAWN_CREATURE" then
		local okl, leader = pcall(EEex_Sprite_GetInPortrait, 0)
		if not okl or leader == nil then
			infai_act_emit(req.action_id, "REFUSED", nil, "NO_PARTY")
			return
		end
		local x, y = req.x, req.y
		if x < 0 then
			local okp = pcall(function() x, y = leader.m_pos.x + 60, leader.m_pos.y + 30 end)
			if not okp then
				infai_act_emit(req.action_id, "REFUSED", nil, "NO_POINT")
				return
			end
		end
		local action = string.format('CreateCreature("%s",[%d.%d],%d)', req.cre, x, y, req.facing)
		local okq = pcall(EEex_Action_ExecuteResponseStringOnAIBaseInstantly, action, leader)
		if not okq then
			infai_act_emit(req.action_id, "REFUSED", nil, "QUEUE_FAILED")
			return
		end
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
	st.check = { id = req.action_id, name = req.name, before = before, at = now + INFAI_ACT_CHECK_MS }
end

-- Chamado a cada frame pelo menu oculto INFAI_ACT_Menu (INFAIAM.menu). Retorna false.
function INFAI_ACT_Tick()
	local st = INFAI_ACT_State
	local now = Infinity_GetClockTicks()
	if st.check ~= nil and now >= st.check.at then
		local area = infai_act_area()
		local count, seen, before = nil, nil, st.check.before
		if area ~= nil then
			local found
			found, seen = infai_act_find(area, st.check.name)
			count = #found
			if st.check.op == "SET_HOSTILE" then        -- vivas (before) e hostis (observed)
				before = #found
				count = 0
				for _, sprite in ipairs(found) do
					if infai_act_hostile(sprite) then count = count + 1 end
				end
			end
		end
		infai_act_emit(st.check.id, "DONE", count, nil, before, seen)
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
