# UniversalSynSaveInstance — versão própria

Esta é uma versão publicada no GitHub do proprietário, com o serializador e as dependências principais autocontidos em `saveinstance.luau`.

## Uso via `loadstring`

```lua
local synsaveinstance = loadstring(
    game:HttpGet(
        "https://raw.githubusercontent.com/luaaaaagkkkkkkk/UniversalSynSaveInstance-Custom/main/saveinstance.luau",
        true
    ),
    "saveinstance"
)()

local SaveInstanceOptions = {}
synsaveinstance(SaveInstanceOptions)
```

Também é possível passar opções aceitas pelo módulo:

```lua
local synsaveinstance = loadstring(game:HttpGet(
    "https://raw.githubusercontent.com/luaaaaagkkkkkkk/UniversalSynSaveInstance-Custom/main/saveinstance.luau",
    true
), "saveinstance")()

synsaveinstance({
    SafeMode = true,
    DecompileTimeout = 15,
    SaveBytecode = true,
})
```

O arquivo `saveinstance.lua` é apenas um wrapper de compatibilidade; para `loadstring`, use diretamente `saveinstance.luau`.

## Observações

O script requer um executor compatível com `loadstring`, `game:HttpGet` e as APIs opcionais usadas pelas opções escolhidas. A disponibilidade de decompilação, propriedades ocultas, clipboard e gravação de arquivos depende do executor.

## Licença

Consulte [`LICENSE`](LICENSE). Este projeto mantém os avisos e atribuições exigidos pela licença original.
