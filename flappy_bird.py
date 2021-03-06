import pygame as pg
import neat
import random
import time
import os

pg.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800
FLOOR = 730
gen = 0

BIRD_IMAGES = [pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bird1.png"))),
               pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bird2.png"))),
               pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMAGES = pg.transform.scale2x(pg.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMAGES = pg.transform.scale2x(pg.image.load(os.path.join("imgs", "base.png")))
BG_IMAGES = pg.transform.scale2x(pg.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pg.font.SysFont("comicsans", 50)


class Bird:
    """
    This class represents the bird
    """
    IMGS = BIRD_IMAGES
    MAX_ANGLE = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Initialization
        :param x: starting x from which it starts (int)
        :param y: starting y from which it starts (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        jump the bird
        :return: None
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        move the bird
        :return: None
        """
        self.tick_count += 1

        displacement = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        if displacement >= 16: displacement = 16  # if actual displacement is too high (>16)

        if displacement < 0: displacement -= 2  # we allow more displacement in upward direction

        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ANGLE:
                self.tilt = self.MAX_ANGLE

        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window
        :return: None
        """
        self.img_count += 1

        # In order to animate the bird, just loop through these images
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

        # don't make the wings flip when the bird is nose diving
        if self.tilt < -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2  # this is to ensure continuity in the orientation of wings

        # here we actually display the tilted images:
        rotated_image = pg.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)


    def get_mask(self):
        """
        gives mask of bird image
        :return: None
        """
        return pg.mask.from_surface(self.img)


class Pipe:
    """
    This class represents a pipe
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pg.transform.flip(PIPE_IMAGES, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGES

        self.passed = False
        self.set_height()

    def set_height(self):
        """
        sets height of the pipe measured from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        moves the pipe with a velocity
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draws a pair of pipes for top and bottom pipes
        :param win: pygame window
        :return: None
        """
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        """
        checks collision of bird with the pipe
        :param bird: Bird object
        :return: Bool
        """
        # mask is an array of pixels
        bird_mask = bird.get_mask()
        top_mask = pg.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pg.mask.from_surface(self.PIPE_BOTTOM)

        # we provide offset in order to work on shifted images
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # calculate the overlap
        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        return bool(t_point or b_point)


class Base:
    """
    Represents the moving floor of the game
    """
    VEL = 5
    WIDTH = BASE_IMAGES.get_width()
    IMG = BASE_IMAGES

    def __init__(self, y):
        """
        Initialization
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        moves the floor
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        draws the floor by using 2 identical images to make it look like it doesn't end.
        :param win: pygame window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        pg.display.update()


def draw_window(win, birds, pipes, base, score, gen):
    """
    draws the windows for the main game loop
    :param win: pygame window
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score (int)
    :param gen: generation (current)
    :param pipe_ind: index of closest pipe
    :return: None
    """

    win.blit(BG_IMAGES, (0, 0))

    for bird in birds:
        bird.draw(win)

    # current score
    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations number
    score_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # how many alive right now
    score_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    pg.display.update()


def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    global gen
    gen += 1
    nets = []
    ge = []
    birds = []

    for g_id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    win = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pg.time.Clock()  # this is in order to slow down the iterations a bit so they are not too fast for us

    score = 0
    run = True
    while (run and len(birds) > 0):
        clock.tick(30)  # this means at most 30 ticks per second can be executed.

        # Quit if the user quits
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                pg.quit()
                quit()

        # determine whether to use first or second pipe on screen for the neural network input
        pipe_ind = 0
        if (len(birds) > 0):
            if (len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width()):
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1  # give each bird a fitness of 0.1 for each frame it stays alive

            # send bird location, top pipe location and bottom pipe location and determine from network whether to
            # jump or not
            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[
                0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. If over 0.5,jump
                bird.jump()

        rem = []
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                # check for collision
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    ge.pop(x)
                    nets.pop(x)
                if pipe.x < bird.x and not pipe.passed:  # the bird crossed the pipe
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # pipe is off the screen
                rem.append(pipe)
            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(500))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if (bird.y + bird.img.get_height() >= 730 or bird.y < 0):  # hits the ground
                birds.pop(x)
                ge.pop(x)
                nets.pop(x)
        base.move()
        draw_window(win, birds, pipes, base, score, gen)


def run(config_file):
    """
    trains neural network to play the Flappy Bird
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)  # path of this directory
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)