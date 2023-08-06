# GNU MediaGoblin -- federated, autonomous media hosting
# Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mediagoblin.tools.routing import add_route

# Add user profile
add_route(
    "mediagoblin.federation.user",
    "/api/user/<string:username>/",
    "mediagoblin.federation.views:user_endpoint"
)

add_route(
    "mediagoblin.federation.user.profile",
    "/api/user/<string:username>/profile",
    "mediagoblin.federation.views:profile_endpoint"
)

# Inbox and Outbox (feed)
add_route(
    "mediagoblin.federation.feed",
    "/api/user/<string:username>/feed",
    "mediagoblin.federation.views:feed_endpoint"
)

add_route(
    "mediagoblin.federation.user.uploads",
    "/api/user/<string:username>/uploads",
    "mediagoblin.federation.views:uploads_endpoint"
)

add_route(
    "mediagoblin.federation.inbox",
    "/api/user/<string:username>/inbox",
    "mediagoblin.federation.views:feed_endpoint"
)

# object endpoints
add_route(
    "mediagoblin.federation.object",
    "/api/<string:objectType>/<string:id>",
    "mediagoblin.federation.views:object_endpoint"
    )
add_route(
    "mediagoblin.federation.object.comments",
    "/api/<string:objectType>/<string:id>/comments",
    "mediagoblin.federation.views:object_comments"
)

add_route(
    "mediagoblin.webfinger.well-known.host-meta",
    "/.well-known/host-meta",
    "mediagoblin.federation.views:host_meta"
)

add_route(
    "mediagoblin.webfinger.well-known.host-meta.json",
    "/.well-known/host-meta.json",
    "mediagoblin.federation.views:host_meta"
)

add_route(
    "mediagoblin.webfinger.whoami",
    "/api/whoami",
    "mediagoblin.federation.views:whoami"
)
