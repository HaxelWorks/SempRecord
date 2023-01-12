<script lang="ts">
    import { Icon } from "@steeze-ui/svelte-icon";
    import { Settings, Dashboard } from "@steeze-ui/remix-icons";
</script>

<ul class="menu p-4 w-80 bg-base-300 text-base-content">
    <li class="menu-title">
        <span>Menu</span>
    </li>

    <li>
        <!-- svelte-ignore a11y-invalid-attribute -->
        <a href="#" class="menu-item">
            <Icon src={Dashboard} class="w-5 h-5 mr-2" />
            <span>Dashboard</span>
        </a>
    </li>
    <li>
        <!-- svelte-ignore a11y-invalid-attribute -->
        <a href="#" class="menu-item">
            <Icon src={Settings} class="w-5 h-5 mr-2" />
            <span>Settings</span>
        </a>
    </li>

    <!-- divider -->
    <li class="menu-title mt-6">
        <span>Actions</span>
    </li>

    <div class="btn-group flex justify-center">
        <button
            class="btn bg-green-500 hover:bg-green-600 text-white rounded-btn"
        >
            Start
        </button>
        <button
            class="btn bg-orange-500 hover:bg-orange-600 text-white rounded-btn"
        >
            Pause
        </button>
        <button class="btn bg-red-600 hover:bg-red-700 text-white rounded-btn">
            Stop
        </button>
    </div>
</ul>
