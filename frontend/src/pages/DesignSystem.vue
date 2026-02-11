<template>
  <div class="min-h-screen bg-gray-50 p-8 font-sans text-gray-900">
    <div class="max-w-7xl mx-auto space-y-12">
      
      <!-- Header -->
      <div class="border-b border-gray-200 pb-6">
        <h1 class="text-3xl font-bold text-gray-900">Design System</h1>
        <p class="mt-2 text-lg text-gray-600">Core components and style guide.</p>
      </div>

      <!-- Typography -->
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Typography & Colors</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="space-y-4">
                <p class="text-4xl font-bold">Heading 1</p>
                <p class="text-3xl font-bold">Heading 2</p>
                <p class="text-2xl font-bold">Heading 3</p>
                <p class="text-base">Body text. Lorem ipsum dolor sit amet.</p>
                <p class="text-sm text-gray-500">Caption</p>
            </div>
            <div class="grid grid-cols-5 gap-4">
                <div v-for="n in [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]" :key="n" 
                    :class="`h-12 w-full rounded bg-primary-${n} flex items-center justify-center text-xs`"
                    :style="n > 400 ? 'color: white' : 'color: black'"
                >
                    {{ n }}
                </div>
            </div>
        </div>
      </section>

      <!-- Buttons -->
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Buttons</h2>
        <div class="flex flex-wrap gap-4 items-center">
            <Button variant="primary">Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="danger">Danger</Button>
        </div>
        <div class="flex flex-wrap gap-4 items-center">
             <Button variant="primary" size="sm">Small</Button>
            <Button variant="primary" size="md">Medium</Button>
            <Button variant="primary" size="lg">Large</Button>
        </div>
        <div class="flex flex-wrap gap-4 items-center">
            <Button loading>Loading</Button>
            <Button disabled>Disabled</Button>
            <Button :iconLeft="Search">With Icon</Button>
        </div>
      </section>

      <!-- Inputs -->
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Inputs</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Input label="Text" placeholder="Text..." v-model="form.text" />
            <Input label="Email" type="email" placeholder="Email..." v-model="form.email" />
            <Input label="Password" type="password" placeholder="***" v-model="form.password" />
            <Input label="Error" error="Required" v-model="form.error" />
            <Input label="Disabled" disabled modelValue="Disabled" />
            <Input label="Icon" :iconLeft="Search" placeholder="Search..." />
        </div>
      </section>

      <!-- Checks/Toggles -->
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Toggles & Checks</h2>
        <div class="flex flex-wrap gap-8">
            <div class="space-y-4">
                <Checkbox label="Check me" v-model="form.check1" />
                <Checkbox label="Helper text" v-model="form.check2" help="Help." />
            </div>
            <div class="space-y-4">
                <Toggle label="Toggle me" v-model="form.toggle1" />
                <Toggle label="Disabled" disabled />
            </div>
        </div>
      </section>

      <!-- Cards -->
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Cards</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card title="Simple Card">
                <p class="text-gray-600">Card content.</p>
            </Card>
             <Card>
                <template #header><h3 class="font-bold">Slot Header</h3></template>
                <p class="text-gray-600">Content.</p>
                <template #footer><Button size="sm">Footer Action</Button></template>
            </Card>
        </div>
      </section>
      
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Dialogs</h2>
        <div>
            <Button @click="showDialog = true">Open Dialog</Button>
            <Dialog v-model="showDialog" title="Confirm">
                <p class="text-gray-600">Are you sure?</p>
                <template #actions>
                    <Button variant="white" @click="showDialog = false">Cancel</Button>
                    <Button variant="danger" @click="showDialog = false">Confirm</Button>
                </template>
            </Dialog>
        </div>
      </section>

      <!-- Toasts -->
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Toasts</h2>
        <div class="flex flex-wrap gap-4">
            <Button @click="toast.success('Operation successful!', 'Success')">Success</Button>
            <Button @click="toast.error('Something went wrong.', 'Error')" variant="danger">Error</Button>
            <Button @click="toast.warning('Check this out.', 'Warning')" variant="secondary">Warning</Button>
            <Button @click="toast.info('Just some info.', 'Info')" variant="ghost">Info</Button>
        </div>
      </section>

      <!-- Tables -->
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Tables</h2>
        
        <div class="space-y-4">
            <h3 class="font-medium">Basic Table</h3>
            <Table :columns="tableColumns" :data="tableData" />
        </div>

        <div class="space-y-4">
            <h3 class="font-medium">Editable Table (Scoped Slots)</h3>
            <Table :columns="editableColumns" :data="editableData">
                 <template #cell(value)="{ row }">
                      <Input v-model="row.value" class="w-full" />
                 </template>
                 <template #cell(actions)="{ index }">
                      <Button size="sm" variant="danger" @click="editableData.splice(index, 1)">Remove</Button>
                 </template>
            </Table>
            <Button size="sm" variant="secondary" @click="editableData.push({ id: Math.random(), name: 'New Item', value: '' })">Add Row</Button>
        </div>
      </section>
      <!-- Skeleton & Breadcrumbs -->
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Skeleton & Breadcrumbs</h2>
        
        <div class="space-y-4">
            <h3 class="font-medium">Breadcrumbs</h3>
            <Breadcrumbs :items="breadcrumbItems" />
        </div>

        <div class="space-y-4">
            <h3 class="font-medium">Skeleton Loading</h3>
            <div class="flex items-center space-x-4">
                 <Skeleton rounded width="3rem" height="3rem" />
                 <div class="space-y-2">
                     <Skeleton width="10rem" />
                     <Skeleton width="6rem" height="0.8rem" />
                 </div>
            </div>
            <Card>
                <div class="space-y-4">
                     <Skeleton height="2rem" width="40%" />
                     <Skeleton count="3" />
                </div>
            </Card>
        </div>
      </section>

      <!-- Advanced UI: Badge, Avatar, Alert, FileUploader -->
      <section class="space-y-6">
        <h2 class="text-2xl font-semibold border-b pb-2">Advanced UI</h2>
        
        <!-- Badges -->
        <div class="space-y-4">
            <h3 class="font-medium">Badges</h3>
            <div class="flex flex-wrap gap-4">
                <Badge variant="gray">Gray</Badge>
                <Badge variant="primary">Primary</Badge>
                <Badge variant="success">Success</Badge>
                <Badge variant="warning">Warning</Badge>
                <Badge variant="error">Error</Badge>
                <Badge variant="info">Info</Badge>
            </div>
             <div class="flex flex-wrap gap-4 items-center">
                <Badge size="sm">Small</Badge>
                <Badge size="md">Medium</Badge>
                <Badge size="lg">Large</Badge>
            </div>
        </div>

        <!-- Avatars -->
        <div class="space-y-4">
            <h3 class="font-medium">Avatars</h3>
            <div class="flex flex-wrap gap-4 items-end">
                <Avatar size="xs" label="User Name" />
                <Avatar size="sm" label="Ertugrul" />
                <Avatar size="md" label="Admin User" />
                <Avatar size="lg" src="https://avatars.githubusercontent.com/u/9919?s=200&v=4" label="Github" />
                <Avatar size="xl" label="Big User" />
            </div>
        </div>

        <!-- Alerts -->
        <div class="space-y-4">
            <h3 class="font-medium">Alerts</h3>
            <div class="space-y-3">
                <Alert title="Info" type="info">This is an informational message.</Alert>
                <Alert title="Success" type="success">Operation completed successfully.</Alert>
                <Alert title="Warning" type="warning">Please be careful with this action.</Alert>
                <Alert title="Error" type="error" dismissible @dismiss="toast.info('Alert dismissed')">
                    Something went wrong! This alert is dismissible.
                </Alert>
            </div>
        </div>

         <!-- File Uploader -->
        <div class="space-y-4">
            <h3 class="font-medium">File Uploader</h3>
            <div class="max-w-lg">
                <FileUploader label="Upload Documents" multiple />
            </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, h } from 'vue'
import Button from '@/components/Button.vue'
import Input from '@/components/Input.vue'
import Checkbox from '@/components/Checkbox.vue'
import Toggle from '@/components/Toggle.vue'
import Select from '@/components/Select.vue'
import Dialog from '@/components/Dialog.vue'
import Card from '@/components/Card.vue'
import Table from '@/components/Table.vue'
import { useToast } from '@/composables/useToast'
import Skeleton from '@/components/Skeleton.vue'
import Breadcrumbs from '@/components/Breadcrumbs.vue'
import Badge from '@/components/Badge.vue'
import Avatar from '@/components/Avatar.vue'
import Alert from '@/components/Alert.vue'
import FileUploader from '@/components/FileUploader.vue'

const Search = {
  render: () => h('svg', { xmlns:"http://www.w3.org/2000/svg", class: "h-5 w-5", fill:"none", viewBox:"0 0 24 24", stroke:"currentColor" }, [
      h('path', { "stroke-linecap":"round", "stroke-linejoin":"round", "stroke-width":"2", d:"M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" })
  ])
}

const form = reactive({
    text: '', email: '', password: '', error: 'Val', select: 'Option 1',
    check1: true, check2: false, toggle1: true, toggle2: false,
})
const showDialog = ref(false)

const toast = useToast()

const tableColumns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'role', label: 'Role' },
]
const tableData = [
    { id: 1, name: 'John Doe', role: 'Admin' },
    { id: 2, name: 'Jane Smith', role: 'User' },
]

const editableColumns = [
    { key: 'name', label: 'Item Name' },
    { key: 'value', label: 'Value (Editable)' },
    { key: 'actions', label: '', cellClass: 'text-right' },
]
const editableData = reactive([
    { id: 1, name: 'Setting A', value: '100' },
    { id: 2, name: 'Setting B', value: '200' },
])

const breadcrumbItems = [
    { label: 'Home', to: '/' },
    { label: 'Settings', to: '/settings' },
    { label: 'Profile' },
]
</script>
