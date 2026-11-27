-- Launcher for UniversalSynSaveInstance.
local RepoURL = "https://raw.githubusercontent.com/luaaaaagkkkkkkk/UniversalSynSaveInstance-Custom/main/"
local BUILD_ID = "2026.11.27-low-memory-2"
local SourceURL = RepoURL .. "saveinstance.luau?build=" .. BUILD_ID

local ok, source = pcall(game.HttpGet, game, SourceURL, true)
if not ok or type(source) ~= "string" or source == "" then
	error("[USSI] Could not download the module. Check public GitHub access and the repository URL.", 2)
end

local marker = "-- USSI_BUILD_ID: " .. BUILD_ID
if not string.find(source, marker, 1, true) then
	error(
		"[USSI] The remote saveinstance.luau is outdated. Publish the files from this ZIP to the configured GitHub repository, then run this launcher again.",
		2
	)
end

local compiler = loadstring
if type(compiler) ~= "function" then
	error("[USSI] This environment does not provide loadstring.", 2)
end

local module = compiler(source, "saveinstance")()
return function(...)
	return module(...)
end
