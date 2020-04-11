import simpy
import random
import statistics

wait_times = []


class Theater(object):
    def __init__(self, env, num_cashiers, num_servers, num_ushers):
        self.env = env

        # Resources
        self.cashier = simpy.Resource(env, num_cashiers)
        self.server = simpy.Resource(env, num_servers)
        self.usher = simpy.Resource(env, num_ushers)

    # Processes
    def purchase_ticket(self, moviegoer):
        yield self.env.timeout(random.randint(1, 3))

    def check_ticket(self, moviegoer):
        yield self.env.timeout(3/60)

    def sell_food(self, moviegoer):
        yield self.env.timeout(random.randint(1, 5))


# Function to define the customers process workflow
def go_to_movies(env, moviegoer, theater):
    # Customers arrival time to the theater
    arrival_time = env.now

    # Customer purchases a ticket
    with theater.cashier.request() as request:
        yield request
        yield env.process(theater.purchase_ticket(moviegoer))

    # Customer gets ticket checked
    with theater.usher.request() as request:
        yield request
        yield env.process(theater.check_ticket(moviegoer))

    # Customer gets food or not
    if random.choice([True, False]):
        with theater.server.request() as request:
            yield request
            yield env.process(theater.sell_food(moviegoer))

    # Customer enters the theater room
    wait_times.append(env.now - arrival_time)


# Run the theater simulation
def run_theater(env, num_cashiers, num_servers, num_ushers):
    theater = Theater(env, num_cashiers, num_servers, num_ushers)

    # Start with 3 customers in begining
    for moviegoer in range(3):
        env.process(go_to_movies(env, moviegoer, theater))

    while True:
        # Wait 12 seconds before generating a new customer (12/60)
        yield env.timeout(0.20)

        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater))


# Get wait time average
def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)


# Pretty print the wait time
def calculate_wait_time(arrival_times):
    average_wait = statistics.mean(wait_times)
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)


# Get user input
def get_user_input():
    num_cashiers = input("Input # of cashiers working:")
    num_servers = input("Input # of servers working:")
    num_ushers = input("Input # of ushers working:")

    params = [num_cashiers, num_servers, num_ushers]

    # check if all 3 inputs are digits
    if all(str(i).isdigit() for i in params):
        params = [int(x) for x in params]
    else:
        print(
            "The input is not valid. We will be using"
            "\n1 cashier, 1 server, 1 usher"
        )
        params = [1, 1, 1]

    return params


def main():

    # Setup environment
    random.seed(42)
    num_cashiers, num_servers, num_ushers = get_user_input()

    # Run the simulation
    env = simpy.Environment()
    env.process(run_theater(env, num_cashiers, num_servers, num_ushers))
    env.run(until=90)

    # View results
    mins, secs = calculate_wait_time(wait_times)
    print(
        "Running simulation..."
        f"\nThe average wait time is {mins} minutes and {secs} seconds."
    )


if __name__ == '__main__':
    main()
