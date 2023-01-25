import os
import neat
import pygame
import pickle

from game import *


# draws the windows for the main game loop
def draw_AI_play(win, bird, pipes, base, score, gameOver):
    win.blit(BG_IMAGE, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    bird.draw(win)
    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    if gameOver == True:
        over_label = END_FONT.render("GAME OVER", 1, (192, 44, 44))
        win.blit(over_label, (WIN_WIDTH  / 2 - over_label.get_width()  / 2, 
                              WIN_HEIGHT / 2 - over_label.get_height() / 2))

    pygame.display.update()


# Simulate best model for single birds
def test_AI(net: neat.nn.FeedForwardNetwork):
    score = 0
    bird  = Bird(230, 350)
    base  = Base(FLOOR)
    pipes = [Pipe(700, 200)]
    clock = pygame.time.Clock()

    run = True
    gameOver = False
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                print("Your AI scores", score)
                quit()

        # determine whether to use the first or second pipe on the screen for neural network input
        pipe_idx = 0
        if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
            pipe_idx = 1                                         
        bird.move()

        # send bird location, top and bottom pipe location and determine from net (jump or not)
        output = net.activate(
                    (bird.y, abs(bird.y - pipes[pipe_idx].height), 
                    abs(bird.y - pipes[pipe_idx].bottom))
                )
        if output[0] > 0.5:
            bird.jump()

        base.move()
        remove = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            if pipe.collide(bird):
                gameOver = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
        if add_pipe:
            if not gameOver:
                score += 1
            pipes.append(Pipe(WIN_WIDTH, random.randint(180, 200)))
        for pipe in remove:
            pipes.remove(pipe)
        if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
            gameOver = True

        draw_AI_play(WIN, bird, pipes, base, score, gameOver)


# runs the NEAT algorithm to train a neural network to play flappy bird
def test_best_network(config_file):
    with open("./model/best.pickle", "rb") as f:
        winner = pickle.load(f)

    best_net = neat.nn.FeedForwardNetwork.create(winner, config_file)
    test_AI(best_net)


# Path of current working directory
if __name__ == '__main__':
    local_dir   = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    confg = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # test model
    test_best_network(confg)