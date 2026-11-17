-- =====================================================================
-- PROJETO FÍSICO DO BANCO DE DADOS - LOJA DE CUPCAKES (PIT 2)
-- SGBD: PostgreSQL (Supabase) - executar no SQL Editor do Supabase
-- =====================================================================

-- 1. Configurações da loja (registro único, id = 1, Araucária/PR)
CREATE TABLE IF NOT EXISTS configuracoes_loja (
    id                INTEGER PRIMARY KEY CHECK (id = 1),
    chave_pix         TEXT        NOT NULL,
    whatsapp          VARCHAR(20) NOT NULL,
    cep_loja          VARCHAR(8)  NOT NULL,
    codigo_ibge_loja  VARCHAR(7)  NOT NULL
);

INSERT INTO configuracoes_loja (id, chave_pix, whatsapp, cep_loja, codigo_ibge_loja)
VALUES (1, '11999999999', '554199999999', '83702000', '4101804')
ON CONFLICT (id) DO NOTHING;

-- 2. Produtos
CREATE TABLE IF NOT EXISTS produtos (
    id                 SERIAL PRIMARY KEY,
    nome               VARCHAR(100)  NOT NULL,
    descricao          TEXT,
    ingredientes       TEXT          NOT NULL,
    peso_gramas        INTEGER,
    preco              NUMERIC(10,2) NOT NULL CHECK (preco > 0),
    estoque            INTEGER       NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    is_acompanhamento  BOOLEAN       NOT NULL DEFAULT FALSE,
    imagem_url         TEXT,
    criado_em          TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_produtos_vitrine ON produtos (estoque);
CREATE INDEX IF NOT EXISTS idx_produtos_acompanhamento ON produtos (is_acompanhamento);

-- 3. Pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id                   SERIAL PRIMARY KEY,
    numero_pedido        VARCHAR(20)   NOT NULL UNIQUE,
    cliente_nome         VARCHAR(100)  NOT NULL,
    cliente_whatsapp     VARCHAR(20)   NOT NULL,
    cep                  VARCHAR(8)    NOT NULL,
    endereco_rua         VARCHAR(150),
    endereco_numero      VARCHAR(10)   NOT NULL,
    endereco_complemento VARCHAR(100),
    endereco_bairro      VARCHAR(100),
    endereco_cidade      VARCHAR(100),
    valor_produtos       NUMERIC(10,2) NOT NULL CHECK (valor_produtos >= 0),
    valor_frete          NUMERIC(10,2) NOT NULL DEFAULT 20.00,
    valor_total          NUMERIC(10,2) NOT NULL CHECK (valor_total >= 0),
    status               VARCHAR(30)   NOT NULL DEFAULT 'Aguardando Pagamento'
        CHECK (status IN ('Aguardando Pagamento', 'Pago / Em Preparo',
                          'Saiu para Entrega', 'Entregue', 'Cancelado')),
    criado_em            TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_pedidos_numero ON pedidos (numero_pedido);
CREATE INDEX IF NOT EXISTS idx_pedidos_status ON pedidos (status);

-- 4. Itens do pedido
CREATE TABLE IF NOT EXISTS itens_pedido (
    id             SERIAL PRIMARY KEY,
    pedido_id      INTEGER       NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
    produto_id     INTEGER       NOT NULL REFERENCES produtos (id) ON DELETE RESTRICT,
    quantidade     INTEGER       NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10,2) NOT NULL CHECK (preco_unitario > 0),
    observacao     VARCHAR(50)
);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido ON itens_pedido (pedido_id);

-- 5. Avaliações (no máximo uma por produto em cada pedido)
CREATE TABLE IF NOT EXISTS avaliacoes (
    id          SERIAL PRIMARY KEY,
    produto_id  INTEGER   NOT NULL REFERENCES produtos (id) ON DELETE CASCADE,
    pedido_id   INTEGER   NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
    nota        INTEGER   NOT NULL CHECK (nota BETWEEN 1 AND 5),
    comentario  TEXT,
    criado_em   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_avaliacao_pedido_produto UNIQUE (pedido_id, produto_id)
);
CREATE INDEX IF NOT EXISTS idx_avaliacoes_produto ON avaliacoes (produto_id);

-- 6. Bucket público de imagens no Supabase Storage
INSERT INTO storage.buckets (id, name, public)
VALUES ('cupcakes-imagens', 'cupcakes-imagens', TRUE)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Leitura publica das imagens de cupcakes"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'cupcakes-imagens');

-- =====================================================================
-- FIM DO PROJETO FÍSICO
-- =====================================================================
