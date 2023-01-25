import pygame
import random
import os

# constants
FLOOR = 730
WIN_WIDTH  = 600
WIN_HEIGHT = 800

pygame.font.init()
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT  = pygame.font.SysFont("comicsans", 70)

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

BG_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg.png")).convert_alpha(), (600, 900))
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "pipe.png")).convert_alpha())
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("assets", "base.png")).convert_alpha())
bird_img = [pygame.transform.scale2x(pygame.image.load(os.path.join("assets", f"bird{i}.png"))) for i in range(1, 4)]


class Bird:
    IMGS = bird_img
    MAX_ROTATION = 25           # how much the bird is gonna tilt (UP / DOWN)
    ROT_VEL = 20                # how much the bird gonna rotate on each frame
    ANIMATION_TIME = 5          # how long we gonna show each bird animation

    def __init__(self, x, y):
        self.x = x              # Starting X position
        self.y = y              # Starting Y position
        self.tilt = 0           # degrees to tilt
        self.tick_count = 0     # track the bird last jump
        self.vel = 0
        self.img_count = 0
        self.img = self.IMGS[0]
        self.height = self.y

    # make the bird jump, velocity < 0 to jump up
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    # make the bird move every single frame
    def move(self):
        self.tick_count += 1

        # for downward acceleration (how many pixels the bird is moving up or down)
        displacement = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        # terminal velocity (no acceleration)
        if displacement >= 16:
            displacement = (displacement / abs(displacement)) * 16

        # make move up more higher
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        # if tilt the bird up, else tile down
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    # draw the bird on pygame window
    def draw(self, win):
        self.img_count += 1

        # for animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # When bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    # collision for the current image of the bird
    def get_mask(self):
        return pygame.mask.from_surface(self.img)


# move object backward toward the bird
class Pipe():
    VEL = 5

    def __init__(self, x, gap):
        self.x = x
        self.gap = gap
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        # if the bird is already pass
        self.passed = False
        self.set_height()

    # set the height of the pipe, from the top of the screen
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top    = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.gap

    # move pipe based on velocity of the pipe
    def move(self):
        self.x -= self.VEL

    # draw both the top and bottom of the pipe
    def draw(self, win: pygame.Surface):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    # True if a point is colliding with the pipe
    def collide(self, bird: Bird):
        bird_mask   = bird.get_mask()
        top_mask    = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset    = (self.x - bird.x, self.top    - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point    = bird_mask.overlap(top_mask, top_offset)

        if bottom_point or top_point:
            return True

        return False


# move object backward toward the bird
class Base:
    VEL = 5
    IMG = base_img
    WIDTH = base_img.get_width()

    # Represnts the moving floor of the game
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    # move 2 floor so it looks like its scrolling
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    # Draw the floor. This is two images that move together.
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


# Rotate a surface and blit it to the window
def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


# draws the windows for the main game loop
def draw_gameplay(win, bird, pipes, base, score, pause, gameStart, gameOver):
    win.blit(BG_IMAGE, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    if not gameStart:
        bird.draw(win)
        score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
        win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    if pause == True and gameStart == False and gameOver == False:
        pause_label = END_FONT.render("PAUSED", 1, (255, 255, 255))
        win.blit(pause_label, (WIN_WIDTH  / 2 - pause_label.get_width() / 2, 
                               WIN_HEIGHT / 2 - pause_label.get_height()))

    if gameStart == True:
        title_label = END_FONT.render("Flappy Bird", 1, (242, 242, 168))
        win.blit(title_label, (WIN_WIDTH  / 2 - title_label.get_width() / 2, 
                               WIN_HEIGHT / 2 - title_label.get_height() - 100))

        bird.x = WIN_WIDTH / 2 - bird_img[0].get_width() / 2
        bird.y = 350
        bird.draw(win)

        start_label = STAT_FONT.render("Press Any KEY to Play", 1, (255, 255, 255))
        win.blit(start_label, (WIN_WIDTH  / 2 - start_label.get_width() / 2, 
                               WIN_HEIGHT / 2 - start_label.get_height() + 100))

    if gameOver == True:
        over_label = END_FONT.render("GAME OVER", 1, (192, 44, 44))
        win.blit(over_label, (WIN_WIDTH  / 2 - over_label.get_width() / 2, 
                              WIN_HEIGHT / 2 - over_label.get_height()))

        retry_label = STAT_FONT.render("Press R to play again", 1, (255, 255, 255))
        win.blit(retry_label, (WIN_WIDTH  / 2 - retry_label.get_width() / 2, 
                               WIN_HEIGHT / 2 - retry_label.get_height() + 100))

    pygame.display.update()


if __name__ == '__main__':
    clock = pygame.time.Clock()
    bird  = Bird(230, 250)
    base  = Base(FLOOR)
    pipes = [Pipe(600, 200)]

    run       = True
    score     = 0
    record    = 0
    pause     = False
    gameStart = True
    gameOver  = False

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if not gameStart:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not gameOver:
                        bird.jump()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        run = False
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if not gameOver:
                            bird.jump()
                    if event.key == pygame.K_SPACE:
                        pause = True if not pause and not gameOver else False
                    if event.key == pygame.K_r and gameOver:
                        score = 0
                        gameStart = False
                        gameOver  = False
                        bird = Bird(230, 250)
                        pipes = [Pipe(600, 200)]
            if gameStart == True:
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
                    score = 0
                    gameStart = False
                    gameOver  = False
                    bird = Bird(230, 250)
                    pipes = [Pipe(600, 200)]

        if gameStart == True:
            remove = []
            for pipe in pipes:
                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    remove.append(pipe)
                pipe.move()
            for pipe in remove:
                pipes.remove(pipe)
            add_pipe = False
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            if add_pipe:
                pipes.append(Pipe(600, random.randint(180, 300)))
            base.move()

        elif not pause:
            remove = []
            add_pipe = False
            for pipe in pipes:
                if pipe.collide(bird):
                    gameOver = True
                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    remove.append(pipe)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
                pipe.move()
            for pipe in remove:
                pipes.remove(pipe)

            # bird score pass through to the pipe
            if add_pipe == True:
                if not gameOver: score += 1
                pipes.append(Pipe(600, random.randint(180, 300)))

            # hit the ground, game over
            if bird.y + bird.img.get_height() >= 730:
                gameOver = True

            # highest score
            if score > record:
                record = score

            bird.move()
            base.move()

        draw_gameplay(WIN, bird, pipes, base, score, pause, gameStart, gameOver)

    pygame.quit()
    print("Your Highest Score is", record)
    quit()