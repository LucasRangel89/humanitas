# midias/

Aqui mora a **biblioteca de mídias** do painel: videoaulas, cursos, artigos,
resenhas, filmes e podcasts que ajudam a estudar os conceitos das notas.

| Arquivo | O que é |
|---|---|
| `biblioteca.yml` | A fonte única da curadoria — é o único arquivo que se edita à mão |
| `../midias.md` | Página gerada (também publicada no site, em *Biblioteca → Mídias*) |
| `../indices/midias.json` | Versão para máquina, com contagens por tipo e tema |

## Regras

1. **Mídia é apoio, nunca fonte.** A nota continua exigindo obra primária com
   capítulo e página na seção *Trecho de apoio*.
2. **Só entra o que foi aberto e conferido.** `verificado_em` (data) e
   `verificado_como` (`oembed`, `pagina` ou `material-do-autor`) são obrigatórios.
   Para YouTube, o método é a API de oEmbed, que devolve título e canal oficiais:
   `https://www.youtube.com/oembed?url=<link>&format=json`.
3. **Toda entrada se liga a uma nota existente** pelo campo `conceitos`. Se não
   se sabe a qual nota a mídia serve, ela não entra.
4. **Nada de "procure no YouTube por X".** Link direto, título literal, canal.

## Comandos

```bash
make midias    # regenera midias.md e indices/midias.json
make auditar   # cobra verificação, tema, conceito existente e URL repetida
make painel    # roda também o midias
```

O protocolo completo, os cinco pesos e o balanço dos planos antigos estão no
[Guia 11](../docs/11-midias-e-videoaulas.md).
