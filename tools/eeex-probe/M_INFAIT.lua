-- SPDX-License-Identifier: Apache-2.0
-- Infinity AI - caixa de dialogo com texto livre (canal INQUIRY, POC da etapa 0).
--
-- Clique com o botao direito numa criatura fora do grupo (ou INFAI_TALK_KEY_NAME com o cursor
-- sobre ela) abre um painel no estilo do dialogo do jogo; enquanto ele esta aberto o jogo fica
-- pausado, como no dialogo nativo (a pausa so e desfeita se foi a caixa que pausou). Enviar publica no console (espelhado no InfinityLoader.log):
--   INFAI-TALK {"schema":"infinity-ai.talk.v1","req_id":...,"speaker":{...},"text":...,"listeners":[...]}
-- A resposta volta pelo arquivo override\INFAIRSP.lua, gravado pelo servico, que define so a
-- tabela INFAI_TALK_Reply = {req_id=..., speech=...}; o painel descarta o cache do recurso e o
-- rele (Infinity_DoFile) ate o req_id bater. Nada aqui altera o estado do motor: sem variaveis, diario, dialogos ou save.
-- Marcos de quest (ADR-0134): le, sem escrever, so as variaveis globais da lista do servico.
-- Voz (ADR-0127): o botao "Falar" publica INFAI-PTT {START|STOP|CANCEL}; o servico abre o
-- microfone no proprio host, transcreve localmente e devolve estado e texto em override\INFAIPTT.lua
-- (so a tabela INFAI_PTT_State). O texto vai para o campo de edicao para revisao; enviar marca
-- "input":"VOICE". A caixa nunca grava audio.
-- Fala padrao (ADR-0129): ao abrir, a criatura diz uma fala do proprio conjunto de sons, como no
-- clique esquerdo do jogo. O motor toca o proprio audio e mostra o proprio texto (mensagem sobre a
-- cabeca); nada entra na fila de acoes da criatura, e nenhum audio ou texto do jogo sai daqui.

INFAI_TALK_SCHEMA = "infinity-ai.talk.v1"
INFAI_TALK_KEY_NAME = "F9"
INFAI_TALK_RANGE = 448          -- alcance visual padrao de um sprite (EEex_Area.lua)
INFAI_TALK_POLL_MS = 500
INFAI_TALK_TIMEOUT_MS = 60000
INFAI_TALK_MAX_TEXT = 500
INFAI_TALK_MAX_LINES = 40
INFAI_TALK_STATE_DEAD = 0x800
INFAI_TALK_RIGHT_CLICK = true    -- abrir com o botao direito sobre a criatura
INFAI_TALK_DEBUG = true         -- laboratorio: registra teclas e motivos no console (sem texto)
INFAI_PTT_SCHEMA = "infinity-ai.ptt.v1"
INFAI_PTT_WAIT_MS = 10000       -- sem "REC" do servico nesse prazo: microfone indisponivel
INFAI_PTT_BUSY_MS = 40000       -- sem texto nesse prazo depois de parar: transcricao falhou
INFAI_TALK_GREET = true         -- fala padrao da criatura ao abrir a caixa (ADR-0129)
-- Slots do conjunto de sons, pelo nome nos .IDS do proprio jogo (sem numeros fixos aqui).
INFAI_GREET_SELECT = { "SELECT_COMMON1", "SELECT_COMMON2", "SELECT_COMMON3", "SELECT_COMMON4",
	"SELECT_COMMON5", "SELECT_COMMON6" }
INFAI_GREET_MEETING = { "INITIAL_MEETING" }
INFAI_NO_STRREF = 4294967295    -- strref vazio (0xFFFFFFFF)
INFAI_GREET_OPTIONS = {}
INFAI_GREET_OPTIONS.overHead = true   -- texto sobre a cabeca, como no clique esquerdo

local function infai_debug(msg)
	if INFAI_TALK_DEBUG then print("INFAI-TALK-DEBUG " .. msg) end
end

INFAI_TALK_State = INFAI_TALK_State or {
	open = false, speaker = nil, selected_leader = nil, lines = {}, pending = nil,
	sent_at = 0, next_poll = 0, n = 0, ptt = nil, from_voice = false,
}
INFAI_TALK_Input = ""

-- EEex chama este gancho antes de abrir a tooltip (o pergaminho com o nome) de uma criatura;
-- true suprime. Com a caixa aberta, nenhuma tooltip de criatura abre nem segue o cursor; fora
-- dela, vale o que havia antes (o padrao do EEex devolve false).
INFAI_TALK_PrevSuppressTooltip = INFAI_TALK_PrevSuppressTooltip or EEex_Sprite_Hook_CheckSuppressTooltip
function EEex_Sprite_Hook_CheckSuppressTooltip()
	if INFAI_TALK_State.open then return true end
	if INFAI_TALK_PrevSuppressTooltip ~= nil then return INFAI_TALK_PrevSuppressTooltip() end
	return false
end

-- Fecha a tooltip de criatura que ja estava aberta (o cursor estava sobre ela no clique), como
-- fazem o B3EffMen e o B3AttackInfo do proprio EEex. So mexe no cursor da interface, nunca no
-- estado do jogo; repetido nos primeiros quadros, porque o motor pode reabri-la no mesmo quadro.
local function infai_clear_world_tooltip()
	pcall(function()
		local chitin = EEex_EngineGlobal_CBaldurChitin
		if chitin ~= nil and chitin.m_pObjectGame ~= nil then
			chitin.m_pObjectGame.m_tempCursor = 4  -- cursor da interface (B3EffMen): fecha a tooltip
		end
	end)
end
INFAI_TALK_CLEAR_TOOLTIP_FRAMES = 3

local function infai_json_string(s)
	s = string.gsub(s, '[%c"\\]', function(c)
		if c == '"' then return '\\"' end
		if c == '\\' then return '\\\\' end
		return string.format('\\u%04x', string.byte(c))
	end)
	return '"' .. s .. '"'
end

local function infai_json_array(list)
	local parts = {}
	for _, v in ipairs(list) do table.insert(parts, infai_json_string(v)) end
	return "[" .. table.concat(parts, ",") .. "]"
end

local function infai_json_number(value)
	if type(value) ~= "number" or value ~= math.floor(value) then return "null" end
	return string.format("%d", value)
end

local function infai_is_dead(sprite)
	local ok, state = pcall(function() return sprite.m_baseStats.m_generalState end)
	if not ok or type(state) ~= "number" then return nil end
	return math.floor(state / INFAI_TALK_STATE_DEAD) % 2 == 1
end

local function infai_party_ids()
	local ids = {}
	for i = 0, 5 do
		local ok, sprite = pcall(EEex_Sprite_GetInPortrait, i)
		if ok and sprite ~= nil then
			local okid, id = pcall(function() return sprite.m_id end)
			if okid then ids[id] = { portrait = i, sprite = sprite } end
		end
	end
	return ids
end

-- EEex 1.1.0 expoe o ID do lider selecionado; resolvemos o objeto via retratos 0..5.
-- O resultado e apenas candidato a iniciador; validar contra dialogos nativos no laboratorio.
local function infai_selected_leader()
	local ok, info = pcall(function()
		local id = EEex_Sprite_GetSelectedID()
		if type(id) ~= "number" or id < 0 then return nil end
		local member = infai_party_ids()[id]
		if member == nil then return nil end
		local selected = member.sprite
		local script = selected.m_scriptName:get()
		local okchr, chr = pcall(function() return EEex_Sprite_GetActiveStats(selected).m_nCHR end)
		local okbase, chrbase = pcall(function() return selected.m_baseStats.m_CHRBase end)
		return {
			id = id,
			script = (type(script) == "string" and script ~= "None") and script or "",
			name = EEex_Sprite_GetName(selected) or "",
			portrait = member.portrait,
			chr_active = (okchr and type(chr) == "number") and chr or nil,
			chr_base = (okbase and type(chrbase) == "number") and chrbase or nil,
		}
	end)
	if ok then return info end
	infai_debug("falha ao ler lider selecionado: " .. tostring(info))
	return nil
end

-- Criatura sob o cursor: alguem fora do grupo ou um companheiro (retratos 1..5); o protagonista
-- (retrato 0) nao conversa consigo mesmo. Retorna tabela de leitura ou nil.
local function infai_speaker_under_cursor()
	local ok, info = pcall(function()
		local object = EEex_GameObject_GetUnderCursor()
		if object == nil or object.m_baseStats == nil then return nil end
		local member = infai_party_ids()[object.m_id]
		if member ~= nil and member.portrait == 0 then return nil end
		local script = object.m_scriptName:get()
		local okcre, cre = pcall(function() return object.m_resref:get() end)
		-- Sabedoria e Inteligencia da ficha (ADR-0117): profundidade do que a pessoa entende.
		local okwis, wis = pcall(function() return EEex_Sprite_GetActiveStats(object).m_nWIS end)
		local okint, int = pcall(function() return EEex_Sprite_GetActiveStats(object).m_nINT end)
		local okchr, chr = pcall(function() return EEex_Sprite_GetActiveStats(object).m_nCHR end)
		local okchrbase, chrbase = pcall(function() return object.m_baseStats.m_CHRBase end)
		local okmorale, morale = pcall(function() return object.m_baseStats.m_morale end)
		local okmbreak, mbreak = pcall(function() return EEex_Sprite_GetActiveStats(object).m_nMoraleBreak end)
		local okmbreakbase, mbreakbase = pcall(function() return object.m_baseStats.m_moraleBreak end)
		return {
			id = object.m_id,
			script = (type(script) == "string" and script ~= "None") and script or "",
			name = EEex_Sprite_GetName(object) or "",
			cre = (okcre and type(cre) == "string") and cre or "",
			dead = infai_is_dead(object),
			party = member ~= nil,
			wis = (okwis and type(wis) == "number") and wis or 0,
			int = (okint and type(int) == "number") and int or 0,
			chr_active = (okchr and type(chr) == "number") and chr or nil,
			chr_base = (okchrbase and type(chrbase) == "number") and chrbase or nil,
			engine_morale_current = (okmorale and type(morale) == "number") and morale or nil,
			engine_morale_break_active = (okmbreak and type(mbreak) == "number") and mbreak or nil,
			engine_morale_break_base = (okmbreakbase and type(mbreakbase) == "number") and mbreakbase or nil,
			x = object.m_pos.x, y = object.m_pos.y,
			sprite = object,    -- so para a fala padrao; nunca vai para o JSON
		}
	end)
	if ok then
		if info == nil then infai_debug("ninguem com quem conversar sob o cursor") end
		return info
	end
	infai_debug("falha ao ler a criatura sob o cursor: " .. tostring(info))
	return nil
end

-- Companheiros (retratos 1..5) ao alcance e com linha de visao do falante.
local function infai_listeners(speaker)
	local names = {}
	local ok = pcall(function()
		local area = EEex_Area_GetVisible()
		local near = EEex_Area_GetAllOfTypeStringInRange(area, speaker.x, speaker.y, "[PC]",
			INFAI_TALK_RANGE, true, false)
		local party = infai_party_ids()
		for _, sprite in ipairs(near) do
			local member = party[sprite.m_id]
			if member ~= nil and member.portrait >= 1 then
				local name = sprite.m_scriptName:get()
				if type(name) == "string" and name ~= "" and name ~= "None" then
					table.insert(names, name)
				end
			end
		end
	end)
	table.sort(names)
	if ok then return names end
	return nil
end

local function infai_add_line(text)
	local st = INFAI_TALK_State
	table.insert(st.lines, text)
	while #st.lines > INFAI_TALK_MAX_LINES do table.remove(st.lines, 1) end
end

local function infai_layout()
	local w, h = Infinity_GetScreenSize()
	local pw = math.min(760, w - 40)
	local ph = 300
	local x, y = math.floor((w - pw) / 2), h - ph - 120
	-- Camada invisivel na tela toda, por baixo da caixa: segura o mouse para o mundo nao
	-- receber o "passar por cima" e o nome da criatura nao seguir o cursor.
	Infinity_SetArea("INFAI_TALK_Shield", 0, 0, w, h)
	Infinity_SetArea("INFAI_TALK_Bg", x, y, pw, ph)
	Infinity_SetArea("INFAI_TALK_Title", x + 16, y + 10, pw - 32, 26)
	Infinity_SetArea("INFAI_TALK_History", x + 16, y + 42, pw - 32, ph - 130)
	Infinity_SetArea("INFAI_TALK_EditBg", x + 16, y + ph - 80, pw - 32, 30)
	Infinity_SetArea("INFAI_TALK_Edit", x + 22, y + ph - 76, pw - 44, 24)
	Infinity_SetArea("INFAI_TALK_Send", x + pw - 236, y + ph - 40, 100, 28)
	Infinity_SetArea("INFAI_TALK_Close", x + pw - 120, y + ph - 40, 100, 28)
	Infinity_SetArea("INFAI_TALK_PTT", x + 16, y + ph - 40, 260, 28)
end

-- Pausa como o dialogo nativo; so despausa o que a propria caixa pausou.
local function infai_pause(on)
	local st = INFAI_TALK_State
	pcall(function()
		local paused = worldScreen:CheckIfPaused()
		if on and not paused then
			EEex_GameState_TogglePause(false, false)
			st.paused_by_box = true
		elseif not on and st.paused_by_box then
			if paused then EEex_GameState_TogglePause(false, false) end
			st.paused_by_box = false
		end
	end)
end

-- Indices do conjunto de sons da ficha, pelo nome: SNDSLOT.IDS (posicoes na ficha) e, se faltar o
-- nome la, SOUNDOFF.IDS. Lidos uma vez; so os numeros sao usados.
INFAI_GREET_IDS = { "SNDSLOT", "SOUNDOFF" }
local infai_slots = nil
local function infai_load_slots()
	infai_slots = {}
	for _, resref in ipairs(INFAI_GREET_IDS) do
		local map = {}
		local ok, err = pcall(function()
			local ids = EEex_Resource_LoadIDS(resref)
			EEex_Resource_IterateUnpackedIDSEntries(ids, function(id, line)
				if type(line) == "string" then map[string.upper(line)] = id end
			end)
		end)
		if not ok then infai_debug(resref .. ".IDS ilegivel: " .. tostring(err)) end
		table.insert(infai_slots, map)
	end
end

local function infai_sound_slot(symbol)
	if infai_slots == nil then infai_load_slots() end
	for _, map in ipairs(infai_slots) do
		if map[symbol] ~= nil then return map[symbol] end
	end
	return nil
end

local function infai_strref(sprite, slot)
	local ok, value = pcall(function() return sprite.m_baseStats.m_speech:get(slot) end)
	if not ok then
		infai_debug("conjunto de sons ilegivel: " .. tostring(value))
		return nil
	end
	if type(value) == "number" and value > 0 and value ~= INFAI_NO_STRREF then return value end
	return nil
end

-- Companheiro: uma fala de selecao; outros: selecao ou, sem ela, a de primeiro encontro.
-- Quem nao tem fala no conjunto de sons (ou esta morto) fica em silencio.
local function infai_greet(speaker)
	if not INFAI_TALK_GREET or speaker.dead ~= false or speaker.sprite == nil then return end
	local groups = { INFAI_GREET_SELECT }
	if not speaker.party then table.insert(groups, INFAI_GREET_MEETING) end
	for _, group in ipairs(groups) do
		local found = {}
		for _, symbol in ipairs(group) do
			local slot = infai_sound_slot(symbol)
			local strref = slot ~= nil and infai_strref(speaker.sprite, slot) or nil
			if strref ~= nil then table.insert(found, strref) end
		end
		if #found > 0 then
			local ok, err = pcall(EEex_Sprite_DisplayTextRef, speaker.sprite,
				found[math.random(#found)], INFAI_GREET_OPTIONS)
			infai_debug("fala padrao: " .. #found .. " opcoes (" .. group[1] .. "), tocada=" ..
				tostring(ok) .. (ok and "" or " erro=" .. tostring(err)))
			return
		end
	end
	if INFAI_TALK_DEBUG then
		-- Laboratorio: quais posicoes da ficha tem fala e onde cada nome caiu (so numeros, sem texto).
		local filled = {}
		for slot = 0, 99 do
			if infai_strref(speaker.sprite, slot) ~= nil then table.insert(filled, tostring(slot)) end
		end
		infai_debug("fala padrao: nenhuma; posicoes com fala=" .. table.concat(filled, ",") ..
			" SELECT_COMMON1=" .. tostring(infai_sound_slot("SELECT_COMMON1")) ..
			" INITIAL_MEETING=" .. tostring(infai_sound_slot("INITIAL_MEETING")))
	end
end

-- O motor guarda em cache o conteudo de override\INFAIRSP.lua (e INFAIPTT.lua) lido na primeira
-- vez; descartar o recurso (como faz EEex_Menu_Eval) obriga a proxima leitura a buscar o arquivo.
-- So estes tres arquivos do servico sao descartados (o terceiro e a lista de variaveis, ADR-0134).
local function infai_drop_cached(resref)
	if resref ~= "INFAIRSP" and resref ~= "INFAIPTT" and resref ~= "INFAIQST" then
		return false, "recurso nao permitido"
	end
	return pcall(function()
		local res = EEex_Resource_Fetch(resref, "LUA")
		if res ~= nil then EngineGlobals.dimmDump(res) end
	end)
end

-- ADR-0134: variaveis do jogo que a caixa pode ler, so as da lista do servico (override\INFAIQST.lua,
-- tabela INFAI_QUEST_Probes = { {id=..., name=...}, ... }), relida a cada abertura. A leitura e so
-- busca na tabela de globais (EEex_Variable_Find nao cria nada); variavel ausente vai como null,
-- nunca como 0. Nada e escrito, e nenhum outro nome e consultado.
INFAI_QUEST_MAX_PROBES = 16

local function infai_quest_load()
	INFAI_QUEST_Probes = nil
	infai_drop_cached("INFAIQST")
	pcall(Infinity_DoFile, "INFAIQST")
end

local function infai_quest_probes()
	local list = INFAI_QUEST_Probes
	if type(list) ~= "table" or #list == 0 then return "null" end
	local hash = nil
	pcall(function() hash = EEex_EngineGlobal_CBaldurChitin.m_pObjectGame.m_variables end)
	local parts = {}
	for i, p in ipairs(list) do
		if i > INFAI_QUEST_MAX_PROBES then break end
		if type(p) == "table" and type(p.id) == "string" and type(p.name) == "string"
				and string.match(p.id, "^[a-z0-9][a-z0-9%-]*$") and #p.id <= 32
				and string.match(p.name, "^[%w_#%-]+$") and #p.name <= 32 then
			local value = nil
			if hash ~= nil then
				local ok, v = pcall(function()
					local found = EEex_Variable_Find(hash, p.name)
					if found == nil then return nil end
					return found.m_intValue
				end)
				if ok then value = v end
			end
			table.insert(parts, infai_json_string(p.id) .. ":" .. infai_json_number(value))
		end
	end
	return "{" .. table.concat(parts, ",") .. "}"
end

function INFAI_TALK_Open()
	local st = INFAI_TALK_State
	if st.open then return false end
	local speaker = infai_speaker_under_cursor()
	if speaker == nil then return false end
	local selected_leader = infai_selected_leader()
	st.open, st.speaker, st.selected_leader, st.lines, st.pending =
		true, speaker, selected_leader, {}, nil
	st.ptt, st.from_voice = nil, false
	-- ADR-0123: um id por abertura da caixa; a conversa vale enquanto ela estiver aberta.
	st.conv = string.format("%d-%d", (INFAI_P2_State and INFAI_P2_State.session_seq) or 0,
		Infinity_GetClockTicks())
	INFAI_TALK_Input = ""
	infai_quest_load()
	if speaker.dead then infai_add_line("(" .. speaker.name .. " não pode responder.)") end
	infai_greet(speaker)
	infai_layout()
	Infinity_PushMenu("INFAI_TALK_Menu")
	infai_clear_world_tooltip()
	st.clear_tooltip = INFAI_TALK_CLEAR_TOOLTIP_FRAMES
	Infinity_FocusTextEdit("INFAI_TALK_Edit")
	infai_pause(true)
	return true
end

local function infai_session_seq()
	return (INFAI_P2_State and INFAI_P2_State.session_seq) or 0
end

-- ADR-0127: um sinal de push-to-talk por linha no console (sem audio, sem texto).
local function infai_ptt_signal(action)
	local st = INFAI_TALK_State
	if st.ptt == nil then return end
	print("INFAI-PTT {" ..
		'"schema":' .. infai_json_string(INFAI_PTT_SCHEMA) ..
		',"ptt_id":' .. infai_json_string(st.ptt.id) ..
		',"action":' .. infai_json_string(action) ..
		',"session_seq":' .. infai_session_seq() ..
		',"clock_ms":' .. string.format("%d", Infinity_GetClockTicks()) .. '}')
end

function INFAI_TALK_Close()
	local st = INFAI_TALK_State
	if not st.open then return end
	if st.ptt ~= nil then infai_ptt_signal("CANCEL") end
	st.ptt, st.from_voice = nil, false
	st.open, st.pending, st.selected_leader = false, nil, nil
	Infinity_PopMenu("INFAI_TALK_Menu")
	infai_pause(false)
end

function INFAI_TALK_Send()
	local st = INFAI_TALK_State
	local text = INFAI_TALK_Input or ""
	text = string.gsub(text, "^%s+", "")
	text = string.gsub(text, "%s+$", "")
	if not st.open or st.pending ~= nil or text == "" or st.speaker.dead then return end
	if #text > INFAI_TALK_MAX_TEXT then text = string.sub(text, 1, INFAI_TALK_MAX_TEXT) end
	local listeners = infai_listeners(st.speaker)
	local selected = st.selected_leader
	local selected_leader_json = "null"
	if selected ~= nil then
		selected_leader_json = '{"script":' .. infai_json_string(selected.script) ..
			',"name":' .. infai_json_string(selected.name) ..
			',"instance":' .. string.format("%d", selected.id) ..
			',"portrait":' .. string.format("%d", selected.portrait) ..
			',"chr_active":' .. infai_json_number(selected.chr_active) ..
			',"chr_base":' .. infai_json_number(selected.chr_base) .. '}'
	end
	local area, game_time = nil, nil
	pcall(function()
		local a = EEex_Area_GetVisible()
		area = a.m_resref:get()
		game_time = a.m_worldTime.m_gameTime
	end)
	local now = Infinity_GetClockTicks()
	st.n = st.n + 1
	local session = (INFAI_P2_State and INFAI_P2_State.session_seq) or 0
	local req_id = string.format("%d-%d-%d", session, now, st.n)
	print("INFAI-TALK {" ..
		'"schema":' .. infai_json_string(INFAI_TALK_SCHEMA) ..
		',"req_id":' .. infai_json_string(req_id) ..
		',"conv":' .. infai_json_string(st.conv or "") ..
		',"session_seq":' .. session ..
		',"clock_ms":' .. string.format("%d", now) ..
		',"area":' .. (area and infai_json_string(area) or "null") ..
		',"game_time":' .. (game_time and string.format("%d", game_time) or "null") ..
		',"input":' .. infai_json_string(st.from_voice and "VOICE" or "TEXT") ..
		',"speaker":{"script":' .. infai_json_string(st.speaker.script) ..
		',"name":' .. infai_json_string(st.speaker.name) ..
		',"cre":' .. infai_json_string(st.speaker.cre) ..
		',"instance":' .. string.format("%d", st.speaker.id) ..
		',"dead":' .. tostring(st.speaker.dead == true) ..
		',"party":' .. tostring(st.speaker.party == true) ..
		',"wis":' .. string.format("%d", st.speaker.wis or 0) ..
		',"int":' .. string.format("%d", st.speaker.int or 0) ..
		',"chr_active":' .. infai_json_number(st.speaker.chr_active) ..
		',"chr_base":' .. infai_json_number(st.speaker.chr_base) ..
		',"engine_morale_current":' .. infai_json_number(st.speaker.engine_morale_current) ..
		',"engine_morale_break_active":' .. infai_json_number(st.speaker.engine_morale_break_active) ..
		',"engine_morale_break_base":' .. infai_json_number(st.speaker.engine_morale_break_base) .. '}' ..
		',"selected_leader":' .. selected_leader_json ..
		',"text":' .. infai_json_string(text) ..
		',"listeners":' .. (listeners and infai_json_array(listeners) or "null") ..
		',"probes":' .. infai_quest_probes() .. '}')
	infai_add_line("Você: " .. text)
	INFAI_TALK_Input = ""
	st.from_voice = false
	st.pending, st.sent_at, st.next_poll = req_id, now, now + INFAI_TALK_POLL_MS
	st.read_error_logged, st.empty_logged = false, false
end


-- ADR-0127: estado do push-to-talk vindo do servico (REC, TEXT, FAILED, CANCELLED).
local function infai_ptt_poll(now)
	local st = INFAI_TALK_State
	local ptt = st.ptt
	if ptt == nil or now < ptt.next_poll then return end
	ptt.next_poll = now + INFAI_TALK_POLL_MS
	INFAI_PTT_State = nil
	infai_drop_cached("INFAIPTT")
	pcall(Infinity_DoFile, "INFAIPTT")
	local s = INFAI_PTT_State
	if type(s) == "table" and s.ptt_id == ptt.id then
		if s.state == "REC" and ptt.phase == "WAIT" then
			ptt.phase, ptt.since = "REC", now
		elseif s.state == "TEXT" and type(s.text) == "string" and s.text ~= "" then
			INFAI_TALK_Input = s.text
			st.from_voice, st.ptt = true, nil
			Infinity_FocusTextEdit("INFAI_TALK_Edit")
			return
		elseif s.state == "FAILED" then
			infai_add_line("(Não entendi; fale de novo ou digite.)")
			st.ptt = nil
			return
		elseif s.state == "CANCELLED" then
			st.ptt = nil
			return
		end
	end
	if ptt.phase == "WAIT" and now - ptt.since > INFAI_PTT_WAIT_MS then
		infai_add_line("(O microfone não respondeu; digite a pergunta.)")
		st.ptt = nil
	elseif ptt.phase == "BUSY" and now - ptt.since > INFAI_PTT_BUSY_MS then
		infai_add_line("(A transcrição não voltou; digite a pergunta.)")
		st.ptt = nil
	end
end

-- Botao "Falar": primeiro clique comeca, segundo clique para (alternancia).
function INFAI_TALK_PTT()
	local st = INFAI_TALK_State
	if not st.open or st.speaker == nil or st.speaker.dead or st.pending ~= nil then return end
	local now = Infinity_GetClockTicks()
	if st.ptt == nil then
		st.n = st.n + 1
		st.ptt = { id = string.format("%d-%d-%d", infai_session_seq(), now, st.n),
			phase = "WAIT", since = now, next_poll = now + INFAI_TALK_POLL_MS }
		infai_ptt_signal("START")
	elseif st.ptt.phase == "WAIT" or st.ptt.phase == "REC" then
		st.ptt.phase, st.ptt.since = "BUSY", now
		infai_ptt_signal("STOP")
	end
end

function INFAI_TALK_PTTText()
	local ptt = INFAI_TALK_State.ptt
	if ptt == nil then return "Falar (microfone)" end
	if ptt.phase == "WAIT" then return "Preparando o microfone..." end
	if ptt.phase == "REC" then return "Gravando... clique para parar" end
	return "Transcrevendo..."
end

-- Chamado a cada frame pelo menu (enabled do rotulo de fundo). Le a resposta, se houver.
function INFAI_TALK_Tick()
	local st = INFAI_TALK_State
	if not st.open then return true end
	if (st.clear_tooltip or 0) > 0 then
		st.clear_tooltip = st.clear_tooltip - 1
		infai_clear_world_tooltip()
	end
	local now = Infinity_GetClockTicks()
	infai_ptt_poll(now)
	if st.pending == nil then return true end
	if now < st.next_poll then return true end
	st.next_poll = now + INFAI_TALK_POLL_MS
	INFAI_TALK_Reply = nil
	local okd, derr = infai_drop_cached("INFAIRSP")
	if not okd and not st.drop_error_logged then
		infai_debug("descartar cache da resposta falhou: " .. tostring(derr))
		st.drop_error_logged = true
	end
	local okf, err = pcall(Infinity_DoFile, "INFAIRSP")
	if not okf and not st.read_error_logged then
		infai_debug("leitura da resposta falhou: " .. tostring(err))
		st.read_error_logged = true
	end
	local reply = INFAI_TALK_Reply
	if type(reply) ~= "table" and not st.empty_logged then
		infai_debug("arquivo de resposta sem tabela (lido=" .. tostring(okf) .. ")")
		st.empty_logged = true
	end
	if type(reply) == "table" and reply.req_id == st.pending and type(reply.speech) == "string" then
		infai_add_line(st.speaker.name .. ": " .. reply.speech)
		st.pending = nil
	elseif now - st.sent_at > INFAI_TALK_TIMEOUT_MS then
		infai_debug("sem resposta para " .. st.pending .. " (ultima lida: " ..
			tostring(type(reply) == "table" and reply.req_id or nil) .. ")")
		infai_add_line("(" .. st.speaker.name .. " não responde.)")
		st.pending = nil
	end
	return true
end

function INFAI_TALK_TitleText()
	local st = INFAI_TALK_State
	return st.speaker and st.speaker.name or ""
end

function INFAI_TALK_HistoryText()
	local text = table.concat(INFAI_TALK_State.lines, "\n\n")
	if INFAI_TALK_State.pending ~= nil then text = text .. "\n\n..." end
	return text
end

function INFAI_TALK_EditAction()
	return 1
end

EEex_Menu_AddMainFileLoadedListener(function()
	EEex_Menu_LoadFile("INFAITLK")
end)

EEex_Key_AddPressedListener(function(key)
	local st = INFAI_TALK_State
	if st.open then
		if key == EEex_Key_GetFromName("Return") then INFAI_TALK_Send()
		elseif key == EEex_Key_GetFromName("Escape") then INFAI_TALK_Close() end
		return
	end
	if key ~= EEex_Key_GetFromName(INFAI_TALK_KEY_NAME) then
		infai_debug("tecla " .. tostring(EEex_Key_GetName(key)))
		return
	end
	if worldScreen ~= e:GetActiveEngine() then infai_debug("fora da tela de mundo"); return end
	if Infinity_TextEditHasFocus() ~= 0 then infai_debug("campo de texto do jogo em foco"); return end
	infai_debug("abrindo")
	INFAI_TALK_Open()
end)

EEex_GameState_AddDestroyedListener(function()
	INFAI_TALK_State.open, INFAI_TALK_State.pending = false, nil
	INFAI_TALK_State.ptt, INFAI_TALK_State.from_voice = nil, false
	INFAI_TALK_State.paused_by_box = false
	INFAI_TALK_State.selected_leader = nil
end)

-- Clique direito: os eventos de mouse passam pelo gancho de eventos do EEex; so o clique direito
-- sobre alguem com quem conversar (fora do grupo ou companheiro), na tela de mundo e com a caixa
-- fechada, e consumido.
local infai_events_poll = EEex_Key_Hook_AfterEventsPoll
function EEex_Key_Hook_AfterEventsPoll(event)
	if INFAI_TALK_RIGHT_CLICK and not INFAI_TALK_State.open then
		local ok, opened = pcall(function()
			if event.type ~= SDL_EventType.SDL_MOUSEBUTTONDOWN or event.button.button ~= 3 then
				return false
			end
			if worldScreen ~= e:GetActiveEngine() then return false end
			return INFAI_TALK_Open()
		end)
		if ok and opened then
			infai_debug("aberta pelo clique direito")
			return true
		end
	end
	return infai_events_poll(event)
end

infai_debug("modulo carregado; tecla " .. INFAI_TALK_KEY_NAME)
