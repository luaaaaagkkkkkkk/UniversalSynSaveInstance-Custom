# UniversalSynSaveInstance — versão própria

Versão própria com `loadstring`, dependências principais locais, progresso detalhado na UI e correções de compatibilidade para serialização binária e atualização do API dump.

## Uso

```lua
local synsaveinstance = loadstring(game:HttpGet(
    "https://raw.githubusercontent.com/luaaaaagkkkkkkk/UniversalSynSaveInstance-Custom/main/saveinstance.lua?",
    true
), "saveinstance-launcher")()

local SaveInstanceOptions = {}
synsaveinstance(SaveInstanceOptions)
```

A compressão fica desativada por padrão para evitar travamentos em executores que implementam zstd/lz4 de forma instável; ela pode ser ativada explicitamente com `CompressionMode = "zstd"` ou `CompressionMode = "lz4"`.

O módulo requer um executor compatível com `loadstring`, `game:HttpGet`, `buffer` e as APIs opcionais escolhidas. A busca de versão usa os endpoints públicos `WindowsStudio64` e não solicita canais beta. O launcher confirma o identificador de build do módulo remoto para impedir que uma cópia antiga seja executada sem aviso.

Consulte [`LICENSE`](LICENSE) para os termos e atribuições.


## Perfil rápido e perfil completo

O padrão prioriza velocidade: não faz decompilação, não recupera scripts publicados como assets e ignora propriedades ocultas do executor. Isso pode deixar `Source` sem o código original e omitir algumas propriedades especiais.

Para priorizar completude em vez de velocidade, use este perfil explícito. Ele evita a lista padrão de exclusões, tenta decompilar todos os scripts acessíveis, recupera fontes publicadas como assets, salva bytecode como fallback e lê propriedades especiais:
```lua
synsaveinstance({
    Decompile = true,
    DecompileTimeout = 10,
    BytecodeTimeout = 10,
    scriptcache = true,
    SaveBytecode = true,
    RecoverScriptsFromAssets = true,
    DecompileIgnore = {},
    IgnoreList = {},
    IgnoreSpecialProperties = false,
    IgnoreDefaultProperties = false,
    IgnoreNotArchivable = false,
    SaveNotCreatable = true,
    NilInstances = true,
    CompressionMode = false,
})
```
O cache usa o bytecode como chave: scripts idênticos são decompilados apenas uma vez, reduzindo o tempo em jogos com cópias do mesmo script. Para máxima velocidade, mantenha o perfil padrão (`Decompile = false`).

Nenhum executor consegue garantir literalmente 100% do conteúdo: scripts server-side filtrados pelo Roblox, propriedades protegidas, instâncias não replicadas e APIs ausentes do executor continuam fora do alcance. Nesses casos o arquivo registra um comentário explicando a limitação ou inclui bytecode quando `SaveBytecode` estiver disponível.
## Atualização obrigatória do arquivo remoto

O arquivo `saveinstance.lua` é um launcher: ele baixa `saveinstance.luau` do repositório GitHub configurado. Apenas extrair este ZIP não altera uma cópia que já esteja publicada no GitHub. Para usar esta correção pelo launcher, publique/substitua no repositório os arquivos `saveinstance.lua` e `saveinstance.luau` desta versão. O launcher usa um identificador de build e interrompe a execução com uma mensagem explícita caso o módulo remoto ainda seja antigo ou esteja em cache.

Ao carregar o módulo corrigido, o console mostra uma mensagem `[USSI] Build ... loaded`. Se essa linha não aparecer, a execução ainda está usando outra cópia do script.

## Correções desta revisão

- Adicionado `StreamBuffer:tostring()` para corrigir a chamada ausente reportada no console.
- Compressão protegida por `pcall`; uma falha do compressor passa a usar chunks sem compressão, em vez de abortar o salvamento.
- Consulta de versão usa endpoints públicos `WindowsStudio64`, sem rota de canal beta, e aproveita diretamente `clientVersionUpload`.
- Cache local do API Dump validado antes de ser aceito.
- Dumpers Python usam downloader compartilhado com timeout, retries, validação de JSON e fallback para versões recentes do `DeployHistory.txt`.
- `Run Dumpers.py` apresenta resumo e retorna código de falha quando algum dumper falha.
