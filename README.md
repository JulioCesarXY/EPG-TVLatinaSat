<p align="center">
  <img src="https://latinasat.com.br/logo.png" alt="Latina Sat Brasil Logo" width="250"/>
</p>

![Atualizar LatinaSat EPG](https://github.com/JulioCesarXY/EPG-TVLatinaSat/actions/workflows/update_epg.yml/badge.svg)
<!-- LAST_UPDATE --> 🕒 **Última Atualização:** `20/06/2026 às 13:20 (BRT)`

---
Script automatizado em Python para extração da grade de programação completa do canal **Latina Sat Brasil** diretamente do código-fonte do site oficial e geração de guia de programação no formato padrão **XMLTV (EPG)**.

## 🚀 Como funciona?

O site da LatinaSat gerencia a programação de forma dinâmica através de uma matriz JavaScript local (`WEEKLY_SCHEDULE`). Este script faz a varredura do código, isola essa estrutura de dados e organiza os programas de forma **cronológica perfeita** (de Domingo a Sábado), tratando corretamente as viradas de horário na madrugada e aplicando o fuso horário correto (`-0300`).

Para garantir que a grade nunca fique desatualizada, o projeto utiliza o **GitHub Actions** para rodar o script de forma autônoma todos os dias de madrugada, commitando o arquivo atualizado diretamente neste repositório.

## 🔗 Link Direto para o Player (M3U8 e EPG)

Para utilizar o Stream, basta copiar e colar a URL abaixo em sua Lista IPTV:

```text
#EXTINF:-1 tvg-id="latinasat.br" tvg-logo="https://latinasat.com.br/logo.png",TV LatinaSat
https://www.latinasat.com.br/hls/live/stream/index.m3u8
```

Para utilizar este guia de programação no seu player de IPTV (como Tivimate, Perfect Player, OTT Navigator, Next.js UI, etc.), basta copiar e colar a URL abaixo:

```text
https://raw.githubusercontent.com/JulioCesarXY/EPG-TVLatinaSat/main/latinasat_epg.xml
```

## ⚙️ Detalhes da Automação (CI/CD)
O workflow do GitHub Actions está configurado para:

Rodar automaticamente todos os dias às 01:00 AM (Horário de Brasília).

Permitir disparo manual direto pela aba Actions do repositório (workflow_dispatch).

Verificar se houve mudanças reais na grade antes de realizar um novo commit para evitar históricos de commits redundantes.

Mantenha o seu guia sempre atualizado rodando de forma perpétua!]

Desenvolvido com ❤️ por JulioCesarXY.
