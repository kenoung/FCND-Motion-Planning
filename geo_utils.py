import matplotlib.pyplot as plt
import tilemapbase

tilemapbase.init(create=True)
t = tilemapbase.tiles.OSM
degree_range = 0.003


def plot_map(current_position):
    extent = tilemapbase.Extent.from_lonlat(current_position[0] - degree_range, current_position[0] + degree_range,
                                            current_position[1] - degree_range, current_position[1] + degree_range)
    extent = extent.to_aspect(1.0)
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    plotter = tilemapbase.Plotter(extent, t, width=600)
    plotter.plot(ax, t, picker=True)
    return fig


def pick_goal(current_position):
    print("pick a goal location")
    goal = []
    fig = plot_map(current_position)
    fig.canvas.mpl_connect('pick_event', callback_maker(goal, fig))
    plt.show()
    return goal[0]


def callback_maker(goal, fig):
    def callback(event):
        evt = event.mouseevent
        plt.clf()
        plt.cla()
        plt.close()
        goal.append(tilemapbase.mapping.to_lonlat(evt.xdata, evt.ydata))
    return callback


def local_pos_to_grid_pos(local_position, north_offset, east_offset):
    return int(local_position[0]) - north_offset, int(local_position[1]) - east_offset


if __name__ == '__main__':
    print(pick_goal((-122.397450, 37.792480)))

    #
    # im = plt.imshow(grid, cmap='gray_r', picker=True)
    # plt.axis((0, grid.shape[1], 0, grid.shape[0]))
    # plt.xlabel("EAST")
    # plt.ylabel("NORTH")
    # plt.scatter(start[1], start[0], marker='x', c='red')
    # fig = plt.gcf()
    # fig.colorbar(im)
    # fig.canvas.mpl_connect('pick_event', callback)
    # plt.gca().set_title("Pickup the goal on the map\n(close the figure to continue)", fontsize=16)
    # plt.show()