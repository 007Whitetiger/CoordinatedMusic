<script lang="ts">
  import logo from './assets/svelte.png';
  import {socket} from "./lib/socket";
  import {onMount} from "svelte";
  let connected = false;
  let started = false;
  let fullyStarted = false;
  let audioElement: HTMLAudioElement;
  let updateInterval: NodeJS.Timer;
  let audioPlace: HTMLDivElement;
  let totalDifference: number = 0;
  let lastUpdated: number;
  let latestDifferenceClientServer: number;
  let searched = 0;
  onMount(() => {
    audioElement = new Audio('/static/clean-bandit.mp3');
    audioElement.load();
    audioElement.controls = true;
    audioPlace.appendChild(audioElement);
    socket.on('connect', () => {
      console.log("Connected to server!");
      connected = true;
    });
    function updateMusic(difference: number) {
      totalDifference += Math.abs(difference - audioElement.currentTime);
      searched++;
      let differenceServer = Math.abs(difference - audioElement.currentTime);
      console.log("difference between server and client: " + differenceServer)
      if (searched < 3 && differenceServer >= 0.3 || searched > 3 && differenceServer >= 0.1) {
          console.log("UPDATING");
          audioElement.currentTime = difference + (totalDifference / searched);
          lastUpdated = difference;
      }
      latestDifferenceClientServer = differenceServer;
    }
    socket.on('broadcast_update', (difference) => {
      if (started) {
        updateMusic(difference)
        console.log("New difference from broadcast: " + difference)
        if (!fullyStarted) {
          audioElement.play();
          fullyStarted = true;
        }
      }
    })
    socket.on('update', (difference) => {
      console.log("New difference: " + difference);
      updateMusic(difference);


    })
  })

  const onStart = () => {
    started = true;
    socket.emit('start');
    updateInterval = setInterval(() => {
        if (!started) return
        socket.emit("update");
    }, 100);
    console.log("Started synchronised songs!")
  }

  const onStop = () => {
    fullyStarted = false;
    started = false;
    clearInterval(updateInterval);
    audioElement.pause();
    console.log("Stopped synchronised songs!");

  }
</script>


<button on:click={onStart}>Start</button>
{lastUpdated} - {latestDifferenceClientServer}
<button on:click={onStop}>stop</button>
<div bind:this={audioPlace}>

</div>
<style>

</style>
