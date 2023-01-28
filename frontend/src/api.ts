import { writable } from "svelte/store";

export interface Recording {
    id: string;
    title: string;
    duration: number;
    date: string;
    thumbnail: string;
}

const API_URL = 'http://127.0.0.1:5000/api';

//get list of recordings
export async function getRecordings(): Promise<Recording[]> {
    const response = await fetch(`${API_URL}/media/recordings`);
    return response.json() as Promise<Recording[]>;
}

export type status = {
    status?: "stopped" | "started" | "paused";
    bitrate?: string;
    drop?: number;
    dup?: number;
    fps?: number;
    frame?: number;
    q?: number;
    size?: string;
    speed?: string;
    time?: string;
}

//make svelte writeable of status object
export const status = writable<status>({});

async function refreshData() {
    const data = await getStatus();
    status.set(data);
}


let gotResults = false;
refreshData();

//trigger every 5 seconds if the previous one finished
setInterval(() => {
    if (!gotResults) {
        refreshData();
    }
    gotResults = false;
}, 5000);

//get status of recording
export async function getStatus(): Promise<status> {
    const response = await fetch(`${API_URL}/status`,{
        method: 'GET',
        cache: 'no-cache',
    });
    const data = await response.json();
    gotResults = true;
    return data as Promise<status>;
}

//start recording
export async function startRecording(): Promise<void> {
    await fetch(`${API_URL}/controls/start`, { method: 'POST' });
}

//stop recording
export async function stopRecording(): Promise<void> {
    await fetch(`${API_URL}/controls/stop`, { method: 'POST' });
}

//pause recording
export async function pauseRecording(): Promise<void> {
    await fetch(`${API_URL}/controls/pause`, { method: 'POST' });
}

