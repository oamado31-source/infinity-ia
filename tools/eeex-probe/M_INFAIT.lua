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
-- O botao "aperte para falar" (push-to-talk, ADR-0107) fica reservado e desabilitado; o campo
-- "input" do protocolo ja preve VOICE.

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

local function infai_debug(msg)
	if INFAI_TALK_DEBUG then print("INFAI-TALK-DEBUG " .. msg) end
end

INFAI_TALK_State = INFAI_TALK_State or {
	open = false, speaker = nil, selected_leader = nil, lines = {}, pending = nil,
	sent_at = 0, next_poll = 0, n = 0,
}
INFAI_TALK_Input = ""

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

function INFAI_TALK_Open()
	local st = INFAI_TALK_State
	if st.open then return false end
	local speaker = infai_speaker_under_cursor()
	if speaker == nil then return false end
	local selected_leader = infai_selected_leader()
	st.open, st.speaker, st.selected_leader, st.lines, st.pending =
		true, speaker, selected_leader, {}, nil
	-- ADR-0123: um id por abertura da caixa; a conversa vale enquanto ela estiver aberta.
	st.conv = string.format("%d-%d", (INFAI_P2_State and INFAI_P2_State.session_seq) or 0,
		Infinity_GetClockTicks())
	INFAI_TALK_Input = ""
	if speaker.dead then infai_add_line("(" .. speaker.name .. " não pode responder.)") end
	infai_layout()
	Infinity_PushMenu("INFAI_TALK_Menu")
	Infinity_FocusTextEdit("INFAI_TALK_Edit")
	infai_pause(true)
	return true
end

function INFAI_TALK_Close()
	local st = INFAI_TALK_State
	if not st.open then return end
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
		',"input":"TEXT"' ..
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
		',"listeners":' .. (listeners and infai_json_array(listeners) or "null") .. '}')
	infai_add_line("Você: " .. text)
	INFAI_TALK_Input = ""
	st.pending, st.sent_at, st.next_poll = req_id, now, now + INFAI_TALK_POLL_MS
	st.read_error_logged, st.empty_logged = false, false
end

-- O motor guarda em cache o conteudo de override\INFAIRSP.lua lido na primeira vez; descartar o
-- recurso (como faz EEex_Menu_Eval) obriga a proxima leitura a buscar o arquivo de novo.
local function infai_drop_cached_reply()
	return pcall(function()
		local res = EEex_Resource_Fetch("INFAIRSP", "LUA")
		if res ~= nil then EngineGlobals.dimmDump(res) end
	end)
end

-- Chamado a cada frame pelo menu (enabled do rotulo de fundo). Le a resposta, se houver.
function INFAI_TALK_Tick()
	local st = INFAI_TALK_State
	if not st.open or st.pending == nil then return true end
	local now = Infinity_GetClockTicks()
	if now < st.next_poll then return true end
	st.next_poll = now + INFAI_TALK_POLL_MS
	INFAI_TALK_Reply = nil
	local okd, derr = infai_drop_cached_reply()
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
