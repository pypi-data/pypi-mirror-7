.. Copyright 2014 Oliver Cope
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..     http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.

CHANGELOG
=========

Version 0.1.5

- Licensing: toffee is now licensed under the Apache License, Version 2.0
- Bugfix: Fixed exception in LazyRecorderFactory.destroy_object during fixture
  teardown

Version 0.1.4

- Added toffee.TestWithFixture

Version 0.1.3

- The data mapper factories (SQLAlchemy and Storm) support querying for
  existing objects in fixtures
- Added experimental SQLAlchemy support

Version 0.1.2

- Made setting factoryoptions more flexible. It's now possible to change the
  default flush/commit behavior of StormFactory per fixture class and or at
  setup time when using the context manager syntax.

Version 0.1.1

- Bugfix: StormFactory did not flush/commit the store on fixture teardown
  teardown, meaning the store would not be left clean for subsequent operations

Version 0.1

- initial release
