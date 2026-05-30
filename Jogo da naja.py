import pygame
import random
import sys
import os

# Inicialização
pygame.init()
pygame.mixer.init()

# Configurações da tela
LARGURA, ALTURA = 800, 600
TAM_CELULA = 40
COLS = LARGURA // TAM_CELULA
ROWS = ALTURA // TAM_CELULA
tela = pygame.display.set_mode((LARGURA, ALTURA))

# Cores
PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
BRANCO = (255, 255, 255)

# Fonte para pontuação
fonte = pygame.font.SysFont("Arial", 30)

# Número de comidas diferentes (máximo 10)
NUM_COMIDAS = 10

# Listas para guardar imagens e sons
imagens_comida = [None] * NUM_COMIDAS
sons_comida = [None] * NUM_COMIDAS

# Cores para quando não houver imagem (cada comida terá uma cor diferente)
cores_fallback = [
    (255, 165, 0),   # laranja
    (255, 0, 0),     # vermelho
    (0, 255, 255),   # ciano
    (255, 255, 0),   # amarelo
    (128, 0, 128),   # roxo
    (0, 128, 0),     # verde escuro
    (255, 192, 203), # rosa
    (165, 42, 42),   # marrom
    (0, 0, 255),     # azul
    (128, 128, 128)  # cinza
]

# Carrega as imagens e sons (0.png a 9.png e 0.wav a 9.wav)
for i in range(NUM_COMIDAS):
    # Imagem
    try:
        img = pygame.image.load(f"{i}.png")
        img = pygame.transform.scale(img, (TAM_CELULA, TAM_CELULA))
        imagens_comida[i] = img
    except:
        imagens_comida[i] = None
        print(f"Aviso: imagem '{i}.png' não encontrada. Usando cor sólida.")

    # Som
    try:
        som = pygame.mixer.Sound(f"{i}.wav")
        sons_comida[i] = som
    except:
        sons_comida[i] = None
        print(f"Aviso: som '{i}.wav' não encontrado. Sem áudio para esta comida.")

# Relógio
clock = pygame.time.Clock()

# Função para gerar nova fruta (posição + tipo aleatório)
def nova_fruta(corpo):
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)
        if (x, y) not in corpo:
            tipo = random.randint(0, NUM_COMIDAS - 1)
            return (x, y, tipo)

# Classe da cobrinha (igual)
class Cobra:
    def __init__(self):
        self.corpo = [(COLS//2, ROWS//2)]
        self.direcao = (1, 0)
        self.crescer = False

    def mover(self):
        cabeca_x, cabeca_y = self.corpo[-1]
        dx, dy = self.direcao
        nova_cabeca = (cabeca_x + dx, cabeca_y + dy)

        if not (0 <= nova_cabeca[0] < COLS and 0 <= nova_cabeca[1] < ROWS):
            return False
        if nova_cabeca in self.corpo[:-1]:
            return False

        self.corpo.append(nova_cabeca)
        if not self.crescer:
            self.corpo.pop(0)
        else:
            self.crescer = False
        return True

    def desenhar(self, tela):
        for i, segmento in enumerate(self.corpo):
            x = segmento[0] * TAM_CELULA
            y = segmento[1] * TAM_CELULA
            cor = (0, 180, 0) if i == len(self.corpo)-1 else VERDE
            pygame.draw.rect(tela, cor, (x, y, TAM_CELULA, TAM_CELULA))
            pygame.draw.rect(tela, PRETO, (x, y, TAM_CELULA, TAM_CELULA), 2)

def desenhar_fruta(tela, fruta):
    x, y, tipo = fruta
    rect = pygame.Rect(x * TAM_CELULA, y * TAM_CELULA, TAM_CELULA, TAM_CELULA)
    if imagens_comida[tipo]:
        tela.blit(imagens_comida[tipo], rect)
    else:
        # Desenha círculo com a cor de fallback
        cor = cores_fallback[tipo % len(cores_fallback)]
        pygame.draw.circle(tela, cor, rect.center, TAM_CELULA//2 - 2)

def desenhar_pontuacao(tela, pontos):
    texto = fonte.render(f"Pontos: {pontos}", True, BRANCO)
    tela.blit(texto, (10, 10))

def tela_game_over(tela, pontos):
    tela.fill(PRETO)
    txt1 = fonte.render("GAME OVER", True, (255, 0, 0))
    txt2 = fonte.render(f"Pontuação final: {pontos}", True, BRANCO)
    txt3 = fonte.render("Pressione ESPAÇO para jogar novamente", True, BRANCO)
    tela.blit(txt1, (LARGURA//2 - txt1.get_width()//2, ALTURA//2 - 60))
    tela.blit(txt2, (LARGURA//2 - txt2.get_width()//2, ALTURA//2 - 20))
    tela.blit(txt3, (LARGURA//2 - txt3.get_width()//2, ALTURA//2 + 20))
    pygame.display.flip()

def main():
    cobra = Cobra()
    fruta = nova_fruta(cobra.corpo)   # (x, y, tipo)
    pontos = 0
    rodando = True
    game_over = False

    while rodando:
        clock.tick(8)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if game_over:
                    if evento.key == pygame.K_SPACE:
                        cobra = Cobra()
                        fruta = nova_fruta(cobra.corpo)
                        pontos = 0
                        game_over = False
                else:
                    if evento.key == pygame.K_UP and cobra.direcao != (0, 1):
                        cobra.direcao = (0, -1)
                    elif evento.key == pygame.K_DOWN and cobra.direcao != (0, -1):
                        cobra.direcao = (0, 1)
                    elif evento.key == pygame.K_LEFT and cobra.direcao != (1, 0):
                        cobra.direcao = (-1, 0)
                    elif evento.key == pygame.K_RIGHT and cobra.direcao != (-1, 0):
                        cobra.direcao = (1, 0)

        if not game_over:
            if not cobra.mover():
                game_over = True

            # Verifica se comeu a fruta (compara apenas posição x, y)
            cabeca = cobra.corpo[-1]
            if (cabeca[0], cabeca[1]) == (fruta[0], fruta[1]):
                cobra.crescer = True
                pontos += 1
                tipo_comida = fruta[2]

                # Toca o áudio correspondente
                if sons_comida[tipo_comida]:
                    sons_comida[tipo_comida].play()

                # Gera nova fruta (posição e tipo aleatórios)
                fruta = nova_fruta(cobra.corpo)

            # Desenha
            tela.fill(PRETO)
            desenhar_fruta(tela, fruta)
            cobra.desenhar(tela)
            desenhar_pontuacao(tela, pontos)
            pygame.display.flip()
        else:
            tela_game_over(tela, pontos)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()