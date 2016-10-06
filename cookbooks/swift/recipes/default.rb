# Copyright (c) 2015 SwiftStack, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


include_recipe "swift::setup"
include_recipe "swift::source"
include_recipe "swift::data"
include_recipe "swift::configs"
include_recipe "swift::rings"

bash "ape-middleware" do
  cwd "/vagrant/ape"
  user "vagrant"
  environment ({'HOME' => '/home/vagrant', 'USER' => 'vagrant'})
  code <<-EOF
    python setup.py build
    sudo python setup.py install
  EOF
end

# start main

execute "startmain" do
  command "sudo -u vagrant swift-init start main"
end

bash "ape-init" do
  cwd "/home/vagrant"
  user "vagrant"
  environment ({'HOME' => '/home/vagrant', 'USER' => 'vagrant'})
  code <<-EOF
    source ~/.profile
    swift post -r '.r:*' test
    swift post -m 'Temp-URL-Key: b3968d0207b54ece87cccc06515a89d4'
  EOF
end
