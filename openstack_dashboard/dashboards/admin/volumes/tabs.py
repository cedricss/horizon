# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from openstack_dashboard.api import cinder
from openstack_dashboard.api import keystone
from openstack_dashboard.dashboards.admin.volumes.volumes \
    import tables as volumes_tables
from openstack_dashboard.dashboards.project.volumes \
    import tabs as volumes_tabs


class VolumeTab(tabs.TableTab, volumes_tabs.VolumeTableMixIn):
    table_classes = (volumes_tables.VolumesTable,
                     volumes_tables.VolumeTypesTable)
    name = _("Volumes")
    slug = "volumes_tab"
    template_name = "admin/volumes/volumes/volumes_tables.html"

    def get_volumes_data(self):
        volumes = self._get_volumes(search_opts={'all_tenants': True})
        instances = self._get_instances(search_opts={'all_tenants': True})
        self._set_attachments_string(volumes, instances)

        # Gather our tenants to correlate against IDs
        try:
            tenants, has_more = keystone.tenant_list(self.request)
        except Exception:
            tenants = []
            msg = _('Unable to retrieve volume project information.')
            exceptions.handle(self.request, msg)

        tenant_dict = SortedDict([(t.id, t) for t in tenants])
        for volume in volumes:
            tenant_id = getattr(volume, "os-vol-tenant-attr:tenant_id", None)
            tenant = tenant_dict.get(tenant_id, None)
            volume.tenant_name = getattr(tenant, "name", None)

        return volumes

    def get_volume_types_data(self):
        try:
            volume_types = cinder.volume_type_list(self.request)
        except Exception:
            volume_types = []
            exceptions.handle(self.request,
                              _("Unable to retrieve volume types"))
        return volume_types


class VolumesGroupTabs(tabs.TabGroup):
    slug = "volumes_group_tabs"
    tabs = (VolumeTab,)
    sticky = True
