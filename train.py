import os
import neat
import pygame
import pickle

from game import *

DRAW_LINES = True
GEN = 0

# draw lines from bird to pipe
def draw_lines(win, pipe_idx):
    try:
        pygame.draw.line(
            win, (255, 0, 0), (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
            (pipes[pipe_idx].x + pipes[pipe_idx].PIPE_TOP.get_width() / 2, pipes[pipe_idx].height), 5
        )
        pygame.draw.line(
            win, (255, 0, 0), (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
            (pipes[pipe_idx].x + pipes[pipe_idx].PIPE_BOTTOM.get_width() / 2, pipes[pipe_idx].bottom), 5
        )
    except BaseException:
        pass


# draws the windows for the main game loop
def draw_window(win, birds, pipes, base, score, gen, pipe_idx):
    if gen == 0: gen = 1
    win.blit(BG_IMAGE, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        if DRAW_LINES:
            draw_lines(win, pipe_idx)

        # draw bird
        bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 70))

    pygame.display.update()


# runs the simulation of the current population of birds and 
# sets their fitness based on the distance they reach in the game
def eval_genomes(genomes, config):
    global GEN
    GEN += 1

    # creating lists of genome, the neural network associated with the genome 
    # and the bird object that uses that network to play
    GE    = []
    nets  = []
    birds = []

    # start with fitness level of 0
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        GE.append(genome)

    score = 0
    base = Base(FLOOR)
    pipes = [Pipe(700, 200)]

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # determine whether to use the first or second pipe on the screen for neural network input
        pipe_idx = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_idx = 1                                              

        # give each bird a fitness of 0.1 for each frame it stays alive
        bird: Bird
        for x, bird in enumerate(birds):
            GE[x].fitness += 0.1
            bird.move()

            # send bird location, top and bottom pipe location and determine from net (jump or not)
            output = nets[birds.index(bird)].activate(
                        (bird.y, abs(bird.y - pipes[pipe_idx].height), 
                        abs(bird.y - pipes[pipe_idx].bottom))
                    )

            # tanh activation function, result will be between -1 and 1
            if output[0] > 0.5:
                bird.jump()

        base.move()

        remove = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()

            # check for collision
            for bird in birds:
                if pipe.collide(bird):
                    GE[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    GE.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1

            # give more reward for passing through a pipe (not required)
            for genome in GE:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH, random.randint(180, 200)))

        for pipe in remove:
            pipes.remove(pipe)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                GE.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, GEN, pipe_idx)

        # break if score gets large enough
        if score > 75:
            break


# Create the population, which is the top-level object for a NEAT run
def train_neat_AI(config_file):
    P = neat.Population(config_file)

    # Add a stdout reporter to show progress in the terminal.
    P.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    P.add_reporter(stats)

    # Run for up to 20 generations.
    winner = P.run(eval_genomes, 20)
    with open("./model/best.pickle", "wb") as f:
        pickle.dump(winner, f)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


# Path of current working directory
if __name__ == '__main__':
    local_dir   = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')

    confg = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
            neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # train model
    train_neat_AI(confg)