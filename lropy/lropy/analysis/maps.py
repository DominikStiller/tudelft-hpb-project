import cartopy.crs as ccrs

from lropy.constants import moon_radius

moon_globe = ccrs.Globe(semimajor_axis=moon_radius, semiminor_axis=moon_radius, ellipse=None)
