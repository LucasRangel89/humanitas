# Guia 01 — Criar o repositório no GitHub (passo a passo para quem nunca usou)

Este guia leva você do zero até o projeto publicado no GitHub usando apenas o navegador. Nenhum comando, nenhum programa para instalar. Reserve cerca de 20 minutos na primeira vez.

## O que é um "repositório"

Pense no repositório como uma **pasta do seu computador que mora na internet**, com três vantagens: nunca se perde, guarda o histórico de tudo o que mudou, e exibe os arquivos de texto de forma bonita e navegável no navegador. Dentro do GitHub, cada projeto é um repositório (ou "repo", para os íntimos).

## Passo 1 — Criar a conta (se você ainda não tem)

1. Acesse `github.com` e clique em **Sign up**.
2. Informe um e-mail, crie uma senha e escolha um **nome de usuário**. Esse nome aparecerá no endereço do seu projeto (por exemplo, `github.com/seu-usuario/painel-ciencias-humanas`), então escolha algo com que você se identifique.
3. Confirme o e-mail de verificação que o GitHub enviará.

## Passo 2 — Criar o repositório

1. Já logado, clique no símbolo **+** no canto superior direito e escolha **New repository**.
2. Preencha assim:
   - **Repository name:** `painel-ciencias-humanas` (ou o nome que preferir; evite espaços e acentos).
   - **Description:** algo como "Painel de estudos autodidata de ciências humanas".
   - **Private ou Public?** Escolha **Private**. Motivo: este projeto contém texto integral de obras protegidas por direitos autorais na pasta `acervo/`. Em um repositório privado, só você vê. Se um dia você quiser compartilhar apenas suas notas e resumos, pode criar outro repositório público com esse material.
   - Marque a opção **Add a README file**.
3. Clique no botão verde **Create repository**.

Pronto: o endereço do seu painel já existe, por exemplo `github.com/seu-usuario/painel-ciencias-humanas`.

## Passo 3 — Subir os arquivos do projeto

Você recebeu um pacote (arquivo `.zip`) com toda a estrutura já pronta. Agora vamos colocá-lo dentro do repositório:

1. No seu computador, **descompacte o arquivo zip** (clique com o botão direito e escolha "Extrair tudo").
2. No GitHub, dentro da página do repositório, clique em **Add file** e depois em **Upload files**.
3. Abra a pasta descompactada, **selecione tudo o que está dentro dela** (pastas `docs`, `templates`, `notebooks`, `acervo` e o `README.md`) e **arraste para a área de upload** do navegador. Use o Chrome ou o Edge: eles mantêm a estrutura de pastas ao arrastar.
4. Espere todos os itens aparecerem na lista e clique em **Commit changes**. ("Commit", aqui, significa simplesmente "salvar no repositório".)

Se o arrastar de pastas não funcionar no seu navegador, há um caminho B: crie cada arquivo manualmente com **Add file > Create new file**. Ao digitar o nome, use a barra `/` para criar pastas — por exemplo, digitar `docs/01-criar-repositorio-no-github.md` já cria a pasta `docs` e o arquivo dentro dela. Copie e cole o conteúdo de cada arquivo do pacote.

Observação: o upload pela interface web aceita até 100 arquivos por vez, o que é mais que suficiente para a estrutura inicial deste projeto.

## Passo 4 — Conferir o resultado

Volte à página inicial do repositório. Você deve ver o `README.md` renderizado como uma página organizada, com tabelas e títulos. Clique nas pastas para navegar. Clicar em `docs/02-fluxo-de-extracao.md` deve mostrar o guia de extração formatado.

Para ler um arquivo Markdown no seu computador sem o GitHub, você pode arrastá-lo para dentro de uma janela do navegador — mas a exibição fica sem formatação. A formatação bonita aparece quando o arquivo está no GitHub, ou em aplicativos como Obsidian e Notion.

## Passo 5 — Marcar o repositório como favorito

Dentro do repositório, clique no ícone de estrela (**Star**) no canto superior direito. Assim ele fica sempre acessível na lista "Your stars" do seu perfil.

## Dicas de nomenclatura para o futuro

Quando você for criar arquivos novos, siga estas convenções — elas evitam problemas com links e nomes quebrados:

- Sem acentos: `sociologia.md` em vez de `sociología.md`.
- Sem espaços: use hífen, como em `max-weber-a-etica-protestante.md`.
- Sempre em letras minúsculas.
- Um livro por arquivo, um conceito por arquivo.

## Próximo passo

Com o repositório criado, siga para o `docs/02-fluxo-de-extracao.md` e comece a transformar seus PDFs no conteúdo do painel.
