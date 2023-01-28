<script lang="ts">
    import { getRecordings, type Recording } from "./api";

    export let allRecordings: Recording[] = [];

    getRecordings().then((recordings) => {
        allRecordings = recordings;
        console.log(recordings);
    });
</script>

<div class="p-6 pb-16">
    <!-- title -->
    <div class="flex justify-between items-center">
        <h1 class="text-3xl font-bold">Dashboard</h1>
    </div>

    <!-- cards grid with thumbnails and some video details -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
        {#each allRecordings as recording}
            <div
                class="card card-compact bg-base-300 shadow-xl hover:cursor-pointer hover:scale-105 transition-transform"
            >
                <figure>
                    <img src={recording.thumbnail} alt="thumbnail" />
                </figure>
                <div class="card-body">
                    <h2 class="card-title first-letter:uppercase">
                        {recording.title}
                    </h2>

                    <div class="card-actions justify-end">
                        <div class="badge badge-outline">
                            {recording.duration}
                        </div>
                        <div class="badge badge-outline">{recording.date}</div>
                    </div>
                </div>
            </div>
        {/each}
    </div>
</div>
