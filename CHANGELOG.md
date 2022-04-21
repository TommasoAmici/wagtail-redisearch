# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2022-04-21

[4c4baba](4c4babaac36ca4246b3c3cec2114bcbcddaa0c6d)...[4125466](4125466ce53625d04b63061d40bbdea7cdd98255)

### Features

- Added support for RelatedFields ([40bc184](40bc184080e6fd331ea339325f2f31359167505d))

## [0.3.3] - 2022-04-20

[ae09850](ae09850d64e7560888251d434547aad1e661b041)...[4c4baba](4c4babaac36ca4246b3c3cec2114bcbcddaa0c6d)

### Bug Fixes

- Applying any ordering would result in empty search results ([e92e091](e92e091162dd9b9d41ee880e1697ca2e8dcab90c))

### Documentation

- Added instructions to install app in Django settings ([af040f8](af040f8f17d891e0251026fd0a1baf9a79c06bcb))

## [0.3.2] - 2022-04-12

[48f93de](48f93de2e765771100a2c340f23bb77afc5d369a)...[ae09850](ae09850d64e7560888251d434547aad1e661b041)

### Bug Fixes

- Specify prefix when creating index ([1328454](132845427b2935cb32b53f56eba47a9137bde9c6))
- Specify index type HASH when creating index ([5807d0a](5807d0a14b65467ae73bdbea0ff5f673fbe1d854))
- To store time as a numeric field it needs to be formatted as a number ([7f71b57](7f71b579c7df93109062a621d04a8ea2d39274f9))

### Styling

- Added isort configuration ([d01440e](d01440e142de381b2612f5daa3d3d7cafd6dadc5))

### Testing

- Added tests for get_redis_field ([09fb82e](09fb82ec648782282c72d405ac2d2fc761585bdc))
- Added fixtures and search tests ([856cec9](856cec96e7bdd37b09ff88bbc5293d2a606a2f86))
- Added autocomplete test ([ab46c81](ab46c81c1b5475b9f00134809f59fba4c718e463))

### Ci

- Always run new tests ([341bd93](341bd93f26a31af9a784ad41980e8fafb94f4165))
- Added redisearch service to test workflows ([bd3e2c7](bd3e2c7e7d81c6aaa87f359f5c01bec2a329738d))

## [0.3.1] - 2022-04-12

[cf919a6](cf919a65ddf992afd843b131172a99dd5dc814b1)...[48f93de](48f93de2e765771100a2c340f23bb77afc5d369a)

### Bug Fixes

- Add_items doesn't expect a fields argument ([09f5c4b](09f5c4b52aa67290671ca8e87bdce4d3f0953d2e))
- Error when converting date objects to timestamps ([0fa7b29](0fa7b29e9d00a102de427ec2102ccf2022386356))
- Error when converting float to redis type ([5ad1bf7](5ad1bf7544f3639a8212c5b82d1c590538305ab3))
- Error when converting time objects to redis type ([2957229](295722935e045efc3d7bab396dad31d7565ebc10))

### Ci

- Use provided cliff config when generating changelog ([caad0ad](caad0ad7032932a1e656c5d1e91ad38e4d003a55))

## [0.3.0] - 2022-04-11

[29d0bf2](29d0bf24638df1ba53bea75b121f390190e6d431)...[cf919a6](cf919a65ddf992afd843b131172a99dd5dc814b1)

### Features

- Added support for more Django field types ([9b3d2f0](9b3d2f0b3d19062f3c28dfc8e1f5320e4a17a898))

### Miscellaneous Tasks

- Added badges to README ([8babce8](8babce8ccf1439abf2d9cddc92981d3b83daf473))

### Ci

- Added codecov action to build workflow ([df5c464](df5c4640b5106947e8aaeb5115eb8d2ce682da4f))

## [0.2.1] - 2022-04-10

[4506df2](4506df29824a91d56c66841c1f26c2be79abc04e)...[29d0bf2](29d0bf24638df1ba53bea75b121f390190e6d431)

### Performance

- Avoid looking up field type and redis field twice for numeric lookups ([728dbd0](728dbd025f2860e7c56721d96c0f83572436bce8))

## [0.2.0] - 2022-04-10

[0a3d1c8](0a3d1c8bba45ddbc9e082d2f58b90136da5471ee)...[4506df2](4506df29824a91d56c66841c1f26c2be79abc04e)

### Breaking changes

- Map Django DateTimeField to NumericField in Redis ([01d9ced](01d9cedb421bfd02475fe08cc3192ea0dcdf07ac))

### Bug Fixes

- Removed print statement when performing a search ([5f21c7a](5f21c7ac343913984b3c67872a7da1314a55f3fb))
- Use NumericField instead of TextField for object IDs ([dc94208](dc942080b192ea66c0102e677d18c6a2efe4215a))

### Features

- Added support for GreaterThan, GreaterThanOrEqual, LessThan, LessThanOrEqual lookups ([7f11e2a](7f11e2a51815fa50732eeba3eb3066471b859ee5))

### Miscellaneous Tasks

- Added rule to identify breaking changes in git cliff config ([ae49df3](ae49df37eb34369baf0989f3f1c349a52057e11c))

### Testing

- Added tests for get_model_root ([2f2b01a](2f2b01a1ffa54fd6440695874a84c72e2492002a))
- Added test for build_filters ([3225fb9](3225fb9c7fb33a9ec06a3f04afa935340a73c912))
- Added test cases to test_build_filters ([c3ed3be](c3ed3beca567a9372af6868eb72b15941c4aab51))

## [0.1.1] - 2022-04-09

[c786930](c7869309a6f88a6ee3698d8118f0948a4ab8c2ba)...[0a3d1c8](0a3d1c8bba45ddbc9e082d2f58b90136da5471ee)

### Documentation

- Updated README with usage instructions ([e771828](e771828734ec949cd8110074cd502634eb5096d5))

### Miscellaneous Tasks

- Updated pyproject.toml with relevant metadata ([76cffaa](76cffaabc0f898c5d250c74ef7f70606082a9088))

### Ci

- When generating changelog fetch entire repo ([1325886](1325886109f1c8f35216452b7d1d2c37ca226339))

## [0.1.0] - 2022-04-09

### Bug Fixes

- Improved handling of lists when converting Python types to Redis types ([ab42689](ab42689747b3fb46260967cac4e31d96424935c2))
- Python < 3.9 needs to import List from typing ([adcb523](adcb5230a01e3b9b0e7fdd49de67a8298785b4bc))
- Support python3.7 as minimum version in pyproject ([4559016](4559016808e3efec14249798d75ed52370b6efb9))

### Features

- Implemented RediSearchModelIndex and rebuilder class ([3f85eba](3f85eba0ef3f0adf66c6ac5ca263a54768cb9084))

### Miscellaneous Tasks

- Added .gitignore for python, visualstudiocode, macos, git ([2d298d6](2d298d6787b5c2a9b262225678a210a54378d2c4))
- Added MIT license ([6c94577](6c94577678848c5cbae35a9b9f0afaebe31b9d3a))
- Initial python commit ([9bcd263](9bcd2634650a95a9576183db1559d32610eae0b6))
- Added pre-commit-config ([dbdb7e4](dbdb7e45e62bc87909198387848aa09ddedd53d8))
- Added vscode settings ([b33ea50](b33ea50f1030c3420ab07d1386357f535df99414))
- Added test rule to Makefile ([66a72a5](66a72a56ad701afbdf0a5241c6209066309438fc))
- Added interface for SearchBackend ([c4804eb](c4804ebe60b01981e9379320d5c06d2dc48d21a5))

### Testing

- Update pytest to v7 ([0c275c7](0c275c774ab8a961d95bee58bcc96fdbf06fde83))
- Added test cases to value_to_redis ([5edc4f9](5edc4f92ab811a662a1948577f07dce5271f94af))
- Set up tox for matrix tests ([5654e7f](5654e7f16b549dc5079c73a39f85615eaba8d2cc))
- Set up pytest to report coverage ([7a3b9da](7a3b9da5c36e2ab997b4f42c74a5f88301e804a4))
- Added doc strings and tests ([8babbb1](8babbb1ea2902c404807d5825dad4430e45286d2))
- Set up django app for integration tests ([e7e28cc](e7e28cc19e6f86e467fc83ddebf9506c3280ec75))
- Added pytest-django to tox.ini ([9bf9aef](9bf9aef86ad30dda9f1a9e4a52bf76cc9da79851))

### Ci

- Added workflow to build and test package ([fff8fca](fff8fca5466fa0938f759c06f65fcdad615dde45))
- Use strings for python version to prevent 3.10 becoming 3.1 ([81cebfa](81cebfaab401f2db4925dd022403e2c648ab9960))
- Install poetry and cache venv ([16bccdc](16bccdc9551603b92d379d0ae373496b81b02f81))
- Run actions when workflows change ([fdf0e7d](fdf0e7d1dd302843445909bbd4a14d94dd00fcb0))
- Install dev dependencies too ([3445a4f](3445a4f3a6a7786b89282e9f7b9fc67b0394eca2))
- Pip install poetry instead of running installation script ([0e880eb](0e880ebca98e619f3f1bd60e2e631039c54b4139))
- Added release workflow for version tags ([58e9d3d](58e9d3ded14539f069311d2a8a98834984f92e80))

<!-- generated by git-cliff -->
