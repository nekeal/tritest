%load_ext autoreload
%autoreload 2
from services import *
from client import *
c = TribalClient("cookie", 153)
c.get_nearest_barbarians_villages()
farm_villages(c, c.barbarians, village_count=2, light_chunk_size=15)
farm_villages(c, c.barbarians, village_count=5, light_chunk_size=15)
c.get_nearest_barbarians_villages(radius=20)
farm_villages(c, c.barbarians, village_count=15, light_chunk_size=15)
len(c.barbarians)
farm_villages(c, c.barbarians, village_count=30, light_chunk_size=4)
farm_villages(c, c.barbarians, village_count=30, light_chunk_size=20)
farm_villages(c, c.barbarians, village_count=30, light_chunk_size=30)
c.barbarians[30]
farm_villages(c, c.barbarians, village_count=100, light_chunk_size=20)
c.barbarians
farm_villages(c, c.barbarians, village_count=100, skip=42, light_chunk_size=10)
farm_villages(c, c.barbarians, village_count=10, skip_count=0, light_chunk_size=1)
farm_villages(c, c.barbarians, village_count=100, skip_count=0, light_chunk_size=1)
farm_villages(c, c.barbarians, village_count=100, skip_count=20, light_chunk_size=10)
farm_villages(c, c.barbarians, village_count=100, skip_count=0, light_chunk_size=10)
get_trip_time_for_all_units_between_cords((515, 498), (508, 503))
ws = WorldSettings('fast', 360, 1)
farm_villages(c, c.barbarians, village_count=100, skip_count=30, light_chunk_size=10)
ws = WorldSettings('fast', 400, 1)
