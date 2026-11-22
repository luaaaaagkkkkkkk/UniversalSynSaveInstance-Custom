-- Compatibility wrapper. Prefer loading saveinstance.luau directly from raw GitHub.
local RepoURL = "https://raw.githubusercontent.com/luaaaaagkkkkkkk/UniversalSynSaveInstance-Custom/main/"
local module = loadstring(game:HttpGet(RepoURL .. "saveinstance.luau", true), "saveinstance")()
return function(...)
	return module(...)
end
