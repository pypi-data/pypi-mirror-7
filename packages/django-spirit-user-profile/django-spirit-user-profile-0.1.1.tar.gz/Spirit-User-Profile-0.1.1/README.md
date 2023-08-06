# Spirit-User-Profile

Integrates Spirit user profile to your **existing** Django user model.

## What this does?

This will insert some fields in your existing User Table that Spirit requires to work properly.

## How?

I followed this [guide](http://django-authtools.readthedocs.org/en/latest/how-to/migrate-to-a-custom-user-model.html).
If you don't want to have yet another installed app (this one), you can follow that guide yourself.
Since I created all the migrations for you, you just need to run some commands and you are done.

## Why?

The old way of joining with a profile table is going away in Django 1.7. This is not true, actually, the old `get_profile()` is going away.
This is for a good reason, let's say you have 4 third-party apps, all using profiles, it would require 4 extra joins to get all the user data.

Would not be easier/better to have all the fields in the same table?

## Dependencies

* Spirit>=0.1.3
* South

## Installing

* Add `south` to your `INSTALLED_APPS`
* Run `python manage.py syncdb`
* Add `spirit_user_profile` to your `INSTALLED_APPS`
* Add `AUTH_USER_MODEL = 'spirit_user_profile.User'` to your `settings.py`

Run:

    python manage.py migrate --fake spirit_user_profile 0001
    python manage.py migrate spirit_user_profile

* Run `python manage.py syncdb` type `no` when it ask you to remove stale auth | user.

Follow the Spirit installation [guide](https://github.com/nitely/Spirit#installing-advanced).

## Copyright / License

Copyright 2014 [Esteban Castro Borsani](https://github.com/nitely).

Licensed under the [MIT License](https://github.com/nitely/Spirit/blob/master/LICENSE).

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.