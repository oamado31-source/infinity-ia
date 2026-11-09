-- SPDX-License-Identifier: Apache-2.0
-- Infinity AI - probe read-only da SPEC-001 (gate P2, ADR-0108 / ADR-0095).
--
-- Publica no console, uma linha por evento, somente os campos da allowlist
-- (host.current_area_id, host.game_time, party.companion_ids):
--   INFAI-P2 {"schema":"infinity-ai.eeex-probe.v1","seq":N,"session_seq":S,"clock_ms":C,"fields":{...}}
-- O InfinityLoader espelha o console no arquivo definido em LogFile=. O probe nao le comandos,
-- nao grava arquivos e nao altera o estado do jogo: so le tres valores e imprime.
-- tests/test_eeex_probe_static.py verifica as funcoes usadas e a ausencia de atribuicoes ao motor.

INFAI_P2_SCHEMA = "infinity-ai.eeex-probe.v1"
INFAI_P2_CHECK_MS = 1000      -- intervalo minimo entre leituras
INFAI_P2_HEARTBEAT_MS = 5000  -- republica mesmo sem mudanca

INFAI_P2_State = { seq = 0, session_seq = 0, next_check = 0, last_emit = -1, last_key = nil }

local function infai_json_string(s)
	s = string.gsub(s, '[%c"\\]', function(c)
		if c == '"' then return '\\"' end
		if c == '\\' then return '\\\\' end
		return string.format('\\u%04x', string.byte(c))
	end)
	return '"' .. s .. '"'
end

local function infai_read_area()
	local ok, value = pcall(function()
		local area = EEex_Area_GetVisible()
		if area == nil then return nil end
		return area.m_resref:get()
	end)
	if ok and type(value) == "string" and value ~= "" then return value end
	return nil
end

local function infai_read_game_time()
	local ok, value = pcall(function()
		return EngineGlobals.g_pBaldurChitin.m_pObjectGame.m_worldTime.m_gameTime
	end)
	if ok and type(value) == "number" then return value end
	return nil
end

-- Companheiros no grupo: script name de cada retrato 1..5 (o retrato 0 e o protagonista, um PC).
-- Retorna lista (possivelmente vazia) ou nil se a leitura falhar.
local function infai_read_companions()
	local ok, value = pcall(function()
		local names = {}
		for i = 1, 5 do
			local sprite = EEex_Sprite_GetInPortrait(i)
			if sprite ~= nil then
				local name = sprite.m_scriptName:get()
				if type(name) == "string" and name ~= "" and name ~= "None" then
					table.insert(names, name)
				end
			end
		end
		table.sort(names)
		return names
	end)
	if ok and type(value) == "table" then return value end
	return nil
end

local function infai_json_array(list)
	if list == nil then return "null" end
	local parts = {}
	for _, name in ipairs(list) do table.insert(parts, infai_json_string(name)) end
	return "[" .. table.concat(parts, ",") .. "]"
end

local function infai_emit(now, area, game_time, companions)
	local st = INFAI_P2_State
	st.seq = st.seq + 1
	local area_json = area and infai_json_string(area) or "null"
	local time_json = game_time and string.format("%d", game_time) or "null"
	print("INFAI-P2 {" ..
		'"schema":' .. infai_json_string(INFAI_P2_SCHEMA) ..
		',"seq":' .. st.seq ..
		',"session_seq":' .. st.session_seq ..
		',"clock_ms":' .. string.format("%d", now) ..
		',"fields":{"host.current_area_id":' .. area_json ..
		',"host.game_time":' .. time_json ..
		',"party.companion_ids":' .. infai_json_array(companions) .. '}}')
	st.last_emit = now
end

-- Chamado a cada frame pelo menu oculto INFAI_P2_Menu (INFAIP2.menu). Retorna false: nada visivel.
function INFAI_P2_Tick()
	local st = INFAI_P2_State
	local now = Infinity_GetClockTicks()
	if now < st.next_check then return false end
	st.next_check = now + INFAI_P2_CHECK_MS

	local area = infai_read_area()
	-- Sem area visivel nao ha partida: tempo (0 no menu) e grupo nao sao observacoes.
	local game_time, companions = nil, nil
	if area ~= nil then
		game_time = infai_read_game_time()
		companions = infai_read_companions()
	end

	local key = tostring(st.session_seq) .. "|" .. tostring(area) .. "|" .. infai_json_array(companions)
	if key ~= st.last_key or st.last_emit < 0 or now - st.last_emit >= INFAI_P2_HEARTBEAT_MS then
		infai_emit(now, area, game_time, companions)
		st.last_key = key
	end
	return false
end

EEex_Menu_AddMainFileLoadedListener(function()
	EEex_Menu_LoadFile("INFAIP2")
end)

local function infai_push_menu()
	Infinity_PushMenu("INFAI_P2_Menu")
end
EEex_GameState_AddInitializedListener(infai_push_menu)
EEex_Menu_AddAfterMainFileReloadedListener(infai_push_menu)

-- Load de save ou volta ao menu encerram a sessao: novo epoch para o bridge.
EEex_GameState_AddDestroyedListener(function()
	INFAI_P2_State.session_seq = INFAI_P2_State.session_seq + 1
	INFAI_P2_State.last_key = nil
end)
