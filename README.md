# Ultimate

## CUC Team History Finder
cucteams.py scrapes the Ultimate Canada website for teams/players that have participated in CUC and determines which teams have most in common with each other.

To run, ensure you have Beautiful Soup 4 installed (pip3 install beatifulsoup4), and run:

`python3 cucteams.py`

For the first run, you will need to pass an additional argument - your login cookie from the CUC website. To get this, log in to canadianultimate.com, then grab the tsid cookie value (in Chrome, go to chrome://settings/cookies/detail?site=canadianultimate.com and grab the "Content" for the tsid cookie). e.g.:

`python3 cucteams.py --tsid_cookie AwAizIlHh7HmjNWqVEL1ow0VHKk23nqH`

Subsequent runs do not require the cookie because the pages are cached. Note that attempting to download everything in one run will likely trigger rate limiting from canadianultimate.com. If this happens, the cache will persist, so you can just wait a minute and re-run each time this happens.

## CUC Gender Scoring Ratios
gender.py scrapes the Ultimate Canada website for genders, scrapes the stats website for stats, and calculates the ratios of points that were thrown/caught by male/female players.

### 2019 Gender Data
#### Overall Stats
Female goals, assists: 1062, 511
Male goals, assists:   1582, 2113
Ratio (male-to-female): goals: 1.4896421845574388, assists: 4.135029354207436

#### Per-team tables

Sorted By Points

| Team                           |   Assist Ratio |   Goal Ratio |   Point Ratio |
|--------------------------------|----------------|--------------|---------------|
| Qold                           |           1.74 |         0.94 |          1.27 |
| 1778                           |           2.48 |         0.9  |          1.45 |
| Notorious KWG                  |           2.23 |         1.31 |          1.69 |
| Fable                          |           3.56 |         1.03 |          1.81 |
| Quest                          |           4.71 |         0.88 |          1.82 |
| Iceberg                        |           3.08 |         1.21 |          1.88 |
| Anchor                         |           6.07 |         0.83 |          1.91 |
| BoD                            |           3.23 |         1.27 |          1.95 |
| Trail Mix                      |           4.29 |         1.14 |          2.04 |
| Happy Campers                  |           4    |         1.2  |          2.05 |
| Mastadon                       |           2.6  |         1.74 |          2.11 |
| Lit                            |           4.86 |         1.16 |          2.15 |
| Spawn                          |           3.08 |         1.58 |          2.16 |
| Union                          |           3.08 |         1.65 |          2.21 |
| Gaia Sale                      |           3.3  |         1.66 |          2.29 |
| Kitchen Party                  |           2.78 |         1.96 |          2.32 |
| Force                          |           6.91 |         1.26 |          2.5  |
| ReUnion                        |           4.64 |         1.55 |          2.51 |
| Quakers                        |           7.36 |         1.24 |          2.54 |
| Khaos                          |           4.6  |         1.71 |          2.65 |
| Victoria Gulls n' Buoys        |           5.55 |         1.65 |          2.67 |
| SOUP                           |           5.12 |         1.7  |          2.74 |
| Red Fox                        |           5.33 |         1.76 |          2.83 |
| Pretty Boys and Handsome Girls |           4.56 |         2.07 |          2.96 |
| Local 613                      |           8.38 |         1.57 |          3    |
| Firefly                        |           4.71 |         2.08 |          3    |
| Battleship                     |          19.25 |         1.31 |          3.1  |
| LAB                            |           3.21 |         3.04 |          3.12 |
| Crux                           |           5    |         2.24 |          3.19 |
| Flux                           |           6.92 |         2.09 |          3.46 |
| T.T                            |           4.41 |         3.09 |          3.65 |
| Penguin Village Ultimate       |           9.5  |         2.65 |          4.42 |

Sorted By Assists

| Team                           |   Assist Ratio |   Goal Ratio |   Point Ratio |
|--------------------------------|----------------|--------------|---------------|
| Qold                           |           1.74 |         0.94 |          1.27 |
| Notorious KWG                  |           2.23 |         1.31 |          1.69 |
| 1778                           |           2.48 |         0.9  |          1.45 |
| Mastadon                       |           2.6  |         1.74 |          2.11 |
| Kitchen Party                  |           2.78 |         1.96 |          2.32 |
| Union                          |           3.08 |         1.65 |          2.21 |
| Iceberg                        |           3.08 |         1.21 |          1.88 |
| Spawn                          |           3.08 |         1.58 |          2.16 |
| LAB                            |           3.21 |         3.04 |          3.12 |
| BoD                            |           3.23 |         1.27 |          1.95 |
| Gaia Sale                      |           3.3  |         1.66 |          2.29 |
| Fable                          |           3.56 |         1.03 |          1.81 |
| Happy Campers                  |           4    |         1.2  |          2.05 |
| Trail Mix                      |           4.29 |         1.14 |          2.04 |
| T.T                            |           4.41 |         3.09 |          3.65 |
| Pretty Boys and Handsome Girls |           4.56 |         2.07 |          2.96 |
| Khaos                          |           4.6  |         1.71 |          2.65 |
| ReUnion                        |           4.64 |         1.55 |          2.51 |
| Quest                          |           4.71 |         0.88 |          1.82 |
| Firefly                        |           4.71 |         2.08 |          3    |
| Lit                            |           4.86 |         1.16 |          2.15 |
| Crux                           |           5    |         2.24 |          3.19 |
| SOUP                           |           5.12 |         1.7  |          2.74 |
| Red Fox                        |           5.33 |         1.76 |          2.83 |
| Victoria Gulls n' Buoys        |           5.55 |         1.65 |          2.67 |
| Anchor                         |           6.07 |         0.83 |          1.91 |
| Force                          |           6.91 |         1.26 |          2.5  |
| Flux                           |           6.92 |         2.09 |          3.46 |
| Quakers                        |           7.36 |         1.24 |          2.54 |
| Local 613                      |           8.38 |         1.57 |          3    |
| Penguin Village Ultimate       |           9.5  |         2.65 |          4.42 |
| Battleship                     |          19.25 |         1.31 |          3.1  |

Sorted By Goals

| Team                           |   Assist Ratio |   Goal Ratio |   Point Ratio |
|--------------------------------|----------------|--------------|---------------|
| Anchor                         |           6.07 |         0.83 |          1.91 |
| Quest                          |           4.71 |         0.88 |          1.82 |
| 1778                           |           2.48 |         0.9  |          1.45 |
| Qold                           |           1.74 |         0.94 |          1.27 |
| Fable                          |           3.56 |         1.03 |          1.81 |
| Trail Mix                      |           4.29 |         1.14 |          2.04 |
| Lit                            |           4.86 |         1.16 |          2.15 |
| Happy Campers                  |           4    |         1.2  |          2.05 |
| Iceberg                        |           3.08 |         1.21 |          1.88 |
| Quakers                        |           7.36 |         1.24 |          2.54 |
| Force                          |           6.91 |         1.26 |          2.5  |
| BoD                            |           3.23 |         1.27 |          1.95 |
| Battleship                     |          19.25 |         1.31 |          3.1  |
| Notorious KWG                  |           2.23 |         1.31 |          1.69 |
| ReUnion                        |           4.64 |         1.55 |          2.51 |
| Local 613                      |           8.38 |         1.57 |          3    |
| Spawn                          |           3.08 |         1.58 |          2.16 |
| Victoria Gulls n' Buoys        |           5.55 |         1.65 |          2.67 |
| Union                          |           3.08 |         1.65 |          2.21 |
| Gaia Sale                      |           3.3  |         1.66 |          2.29 |
| SOUP                           |           5.12 |         1.7  |          2.74 |
| Khaos                          |           4.6  |         1.71 |          2.65 |
| Mastadon                       |           2.6  |         1.74 |          2.11 |
| Red Fox                        |           5.33 |         1.76 |          2.83 |
| Kitchen Party                  |           2.78 |         1.96 |          2.32 |
| Pretty Boys and Handsome Girls |           4.56 |         2.07 |          2.96 |
| Firefly                        |           4.71 |         2.08 |          3    |
| Flux                           |           6.92 |         2.09 |          3.46 |
| Crux                           |           5    |         2.24 |          3.19 |
| Penguin Village Ultimate       |           9.5  |         2.65 |          4.42 |
| LAB                            |           3.21 |         3.04 |          3.12 |
| T.T                            |           4.41 |         3.09 |          3.65 |
