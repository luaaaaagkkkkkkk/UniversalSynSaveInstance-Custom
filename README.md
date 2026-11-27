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

O padrão agora tenta decompilar os scripts e recuperar fontes publicadas como assets. Para reduzir o uso de memória em celulares, o bytecode não é anexado ao código e o cache pesado fica desligado por padrão. Para máxima velocidade, você pode passar `Decompile = false`.

Para priorizar completude em vez de velocidade, use este perfil explícito. Ele evita a lista padrão de exclusões, tenta decompilar todos os scripts acessíveis, recupera fontes publicadas como assets e lê propriedades especiais sem anexar bytecode:
```lua
synsaveinstance({
    Decompile = true,
    DecompileTimeout = 6,
    DecompileMaxSourceBytes = 2 * 1024 * 1024,
    BytecodeTimeout = 10,
    scriptcache = false,
    SaveBytecode = false,
    RecoverScriptsFromAssets = true,
    DecompileIgnore = {},
    IgnoreList = {},
    IgnoreSpecialProperties = false,
    IgnoreDefaultProperties = false,
    IgnoreNotArchivable = false,
    SaveNotCreatable = true,
    CompressionMode = false,
})
```
Para reduzir o uso de memória no mobile, o bytecode não é anexado ao `Source`, o cache fica desligado por padrão, o render 3D é pausado durante o save e fontes acima de 2 MB são limitadas sem inserir mensagem no código salvo. O dump libera memória entre scripts e pausa a decompilação após três falhas consecutivas. Se quiser cache temporário, use `scriptcache = true`; ele é limitado a 4 MB e desaparece ao terminar o save. Para máxima velocidade, use `synsaveinstance({ Decompile = false, RecoverScriptsFromAssets = false, SaveBytecode = false })`.

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
