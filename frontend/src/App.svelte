<script lang="ts">
    import Sidebar from "./Sidebar.svelte";
    import Content from "./Content.svelte";
</script>

<div class="drawer drawer-mobile">
    <input id="sideBtn" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
        <Content />
    </div>
    <div class="drawer-side grid-flow-dense">
        <label for="sideBtn" class="drawer-overlay" />
        <Sidebar />
    </div>
</div>
