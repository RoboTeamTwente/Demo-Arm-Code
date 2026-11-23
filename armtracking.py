from leader import Leader
from follower import Follower
import time

leader = None
follower = None

try:
    leader = Leader(port="/dev/ttyACM0", id="SKYNET")
    follower = Follower(port="/dev/ttyACM1", id="T300")

    while True:
        positions = leader.get_action()
        follower.follower.send_action(positions)
        time.sleep(0.02)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    if follower is not None:
        follower.disconnect()

    if leader is not None:
        leader.disconnect()