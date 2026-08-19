// YouTube Playlist Downloader Pro - Client Logic
document.addEventListener("DOMContentLoaded", () => {
  let currentConfig = {
    default_save_path: "/Volumes/External Storage SSD 1/DJ",
    default_format: "mp3_320k",
    browser_cookies: "none",
    parallel_workers: 5
  };
  let selectedFormat = "mp3_320k";
  let selectedCookies = "none";
  let currentPlaylist = null;
  let isDownloading = false;
  let completedCount = 0;
  let targetFolderCreated = "";

  // Multi-Job Download Manager State
  let downloadJobs = [];
  let currentActiveJob = null;

  // Navigation Tab Elements
  const tabBtnNewPlaylist = document.getElementById("tabBtnNewPlaylist");
  const tabBtnDownloads = document.getElementById("tabBtnDownloads");
  const tabBtnAbout = document.getElementById("tabBtnAbout");
  const viewNewPlaylist = document.getElementById("viewNewPlaylist");
  const viewDownloads = document.getElementById("viewDownloads");
  const viewAbout = document.getElementById("viewAbout");
  const activeDownloadsBadge = document.getElementById("activeDownloadsBadge");
  const downloadJobsList = document.getElementById("downloadJobsList");
  const jobsCountBadge = document.getElementById("jobsCountBadge");

  // Audio Preview Player State
  let currentPreviewVideoId = null;
  const audioElement = document.getElementById("previewAudioElement");
  const audioPlayerBar = document.getElementById("audioPlayerBar");
  const playerThumb = document.getElementById("playerThumb");
  const playerTitle = document.getElementById("playerTitle");
  const playerArtist = document.getElementById("playerArtist");
  const btnPlayPause = document.getElementById("btnPlayPause");
  const playIcon = document.getElementById("playIcon");
  const pauseIcon = document.getElementById("pauseIcon");
  const playerCurrentTime = document.getElementById("playerCurrentTime");
  const playerDuration = document.getElementById("playerDuration");
  const playerSeek = document.getElementById("playerSeek");
  const volumeSlider = document.getElementById("volumeSlider");
  const btnClosePlayer = document.getElementById("btnClosePlayer");

  // DOM Elements
  const savePathDisplay = document.getElementById("savePathDisplay");
  const btnChangePath = document.getElementById("btnChangePath");
  const playlistUrlInput = document.getElementById("playlistUrlInput");
  const btnAnalyze = document.getElementById("btnAnalyze");
  const analyzeBtnText = document.getElementById("analyzeBtnText");
  const formatPills = document.querySelectorAll(".format-pill");
  const cookieSelect = document.getElementById("cookieSelect");

  const overviewCard = document.getElementById("overviewCard");
  const overviewTitle = document.getElementById("overviewTitle");
  const overviewCount = document.getElementById("overviewCount");
  const overviewFolder = document.getElementById("overviewFolder");
  const btnStartDownload = document.getElementById("btnStartDownload");
  const startDownloadBtnText = document.getElementById("startDownloadBtnText");
  const btnReset = document.getElementById("btnReset");

  const workersCard = document.getElementById("workersCard");
  const overallProgressText = document.getElementById("overallProgressText");

  const trackTableBody = document.getElementById("trackTableBody");
  const emptyState = document.getElementById("emptyState");
  const trackCountBadge = document.getElementById("trackCountBadge");
  const selectedCountBadge = document.getElementById("selectedCountBadge");
  const selectAllCheckbox = document.getElementById("selectAllCheckbox");
  const tableSearch = document.getElementById("tableSearch");
  const toastContainer = document.getElementById("toastContainer");

  // API Bridge
  const api = {
    async getConfig() {
      if (window.pywebview && window.pywebview.api) {
        return await window.pywebview.api.get_config();
      }
      const res = await fetch("/api/config");
      return await res.json();
    },
    async saveConfig(config) {
      if (window.pywebview && window.pywebview.api) {
        return await window.pywebview.api.save_config(config);
      }
      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config)
      });
      return await res.json();
    },
    async selectFolder() {
      if (window.pywebview && window.pywebview.api) {
        return await window.pywebview.api.select_folder();
      }
      const res = await fetch("/api/select_folder", { method: "POST" });
      return await res.json();
    },
    async analyzePlaylist(url, browserCookies) {
      if (window.pywebview && window.pywebview.api) {
        return await window.pywebview.api.analyze_playlist(url, browserCookies);
      }
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, browser_cookies: browserCookies })
      });
      return await res.json();
    },
    async getAudioPreview(videoId, browserCookies) {
      if (window.pywebview && window.pywebview.api) {
        return await window.pywebview.api.get_audio_preview(videoId, browserCookies);
      }
      const res = await fetch("/api/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_id: videoId, browser_cookies: browserCookies })
      });
      return await res.json();
    },
    async startDownload(payload) {
      if (window.pywebview && window.pywebview.api) {
        return await window.pywebview.api.start_download(payload);
      }
      const res = await fetch("/api/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      return await res.json();
    },
    async cancelDownload() {
      if (window.pywebview && window.pywebview.api) {
        return await window.pywebview.api.cancel_download();
      }
      const res = await fetch("/api/cancel", { method: "POST" });
      return await res.json();
    },
    async openFolder(folderPath) {
      if (window.pywebview && window.pywebview.api) {
        return await window.pywebview.api.open_folder(folderPath);
      }
      const res = await fetch("/api/open_folder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folder_path: folderPath })
      });
      return await res.json();
    },
    async openUrl(url) {
      if (window.pywebview && window.pywebview.api && window.pywebview.api.open_url) {
        return await window.pywebview.api.open_url(url);
      }
      const res = await fetch("/api/open_url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });
      return await res.json();
    }
  };

  window.onWorkerProgress = function (data) {
    handleWorkerProgress(data);
  };

  window.onDownloadComplete = function (data) {
    handleDownloadComplete(data);
  };

  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        ${type === "success" ? '<polyline points="20 6 9 17 4 12"></polyline>' : 
          type === "error" ? '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>' : 
          '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>'}
      </svg>
      <span>${message}</span>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  }

  async function initConfig() {
    try {
      const cfg = await api.getConfig();
      if (cfg && cfg.default_save_path) {
        currentConfig = cfg;
        savePathDisplay.textContent = cfg.default_save_path;
        if (cfg.default_format) {
          selectedFormat = cfg.default_format;
          formatPills.forEach(p => {
            p.classList.toggle("active", p.dataset.format === selectedFormat);
          });
        }
        if (cfg.browser_cookies && cookieSelect) {
          selectedCookies = cfg.browser_cookies;
          cookieSelect.value = cfg.browser_cookies;
        }
      }
    } catch (e) {
      console.warn("Config load error", e);
    }
  }

  formatPills.forEach(pill => {
    pill.addEventListener("click", () => {
      formatPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      selectedFormat = pill.dataset.format;
      currentConfig.default_format = selectedFormat;
      api.saveConfig(currentConfig);
    });
  });

  if (cookieSelect) {
    cookieSelect.addEventListener("change", () => {
      selectedCookies = cookieSelect.value;
      currentConfig.browser_cookies = selectedCookies;
      api.saveConfig(currentConfig);
      showToast(`Cookie mode: ${selectedCookies}`, "info");
    });
  }

  btnChangePath.addEventListener("click", async () => {
    try {
      const res = await api.selectFolder();
      if (res && res.path) {
        currentConfig.default_save_path = res.path;
        savePathDisplay.textContent = res.path;
        await api.saveConfig(currentConfig);
        showToast(`Save path updated: ${res.path}`, "success");
        if (currentPlaylist) {
          overviewFolder.textContent = `${res.path}/${currentPlaylist.playlist_title}/`;
        }
      }
    } catch (e) {
      showToast("Could not select folder", "error");
    }
  });

  // Analyze Playlist
  btnAnalyze.addEventListener("click", async () => {
    const url = playlistUrlInput.value.trim();
    if (!url) {
      showToast("Please paste a YouTube Playlist URL first.", "error");
      playlistUrlInput.focus();
      return;
    }

    btnAnalyze.disabled = true;
    analyzeBtnText.textContent = "Analyzing...";
    emptyState.style.display = "flex";
    emptyState.innerHTML = `
      <div class="pulse-dot" style="width: 24px; height: 24px; margin-bottom: 8px;"></div>
      <p>Analyzing playlist metadata via yt-dlp... Please wait a few seconds.</p>
    `;
    trackTableBody.innerHTML = "";

    try {
      const res = await api.analyzePlaylist(url, selectedCookies);
      if (res && res.success) {
        currentPlaylist = res;
        // Default all tracks to selected
        currentPlaylist.tracks.forEach(t => t.selected = true);

        overviewTitle.textContent = res.playlist_title;
        overviewCount.textContent = `${res.track_count} Tracks`;
        overviewFolder.textContent = `${currentConfig.default_save_path}/${res.playlist_title}/`;
        overviewCard.style.display = "flex";
        trackCountBadge.textContent = `${res.track_count} Tracks`;

        renderTracklist(res.tracks);
        updateSelectionCounts();
        showToast(`Found ${res.track_count} tracks in "${res.playlist_title}"!`, "success");
      } else {
        showToast(res.error || "Failed to analyze playlist.", "error");
        emptyState.innerHTML = `<p style="color: #ef4444;">Error: ${res.error || "Could not fetch playlist."}</p>`;
      }
    } catch (e) {
      showToast("An error occurred during analysis.", "error");
      emptyState.innerHTML = `<p style="color: #ef4444;">Failed to connect to backend engine.</p>`;
    } finally {
      btnAnalyze.disabled = false;
      analyzeBtnText.textContent = "Analyze Playlist";
    }
  });

  playlistUrlInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      btnAnalyze.click();
    }
  });

  // Render Tracklist Table
  function renderTracklist(tracks) {
    trackTableBody.innerHTML = "";
    emptyState.style.display = "none";
    selectAllCheckbox.checked = true;

    tracks.forEach((track) => {
      const tr = document.createElement("tr");
      tr.id = `trackRow_${track.index}`;
      tr.innerHTML = `
        <td class="col-check">
          <input type="checkbox" class="custom-checkbox track-checkbox" data-index="${track.index}" ${track.selected ? 'checked' : ''} />
        </td>
        <td class="col-num">${String(track.index).padStart(2, "0")}</td>
        <td class="col-thumb">
          <div class="thumb-wrapper" data-id="${track.id}" data-index="${track.index}" title="Click to preview audio">
            <img class="thumb-img" src="${track.thumbnail || 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'40\' height=\'40\'%3E%3Crect width=\'40\' height=\'40\' fill=\'%231a1e2e\'/%3E%3C/svg%3E'}" alt="" loading="lazy" />
            <div class="play-overlay">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            </div>
          </div>
        </td>
        <td class="col-artist">${escapeHtml(track.artist)}</td>
        <td class="col-title">${escapeHtml(track.title)}</td>
        <td class="col-duration">${track.duration_formatted}</td>
        <td class="col-status">
          <span class="badge queued" id="badge_${track.index}" title="Waiting in queue">Queued</span>
        </td>
      `;
      trackTableBody.appendChild(tr);
    });

    // Checkbox events
    document.querySelectorAll(".track-checkbox").forEach(cb => {
      cb.addEventListener("change", (e) => {
        const idx = parseInt(e.target.dataset.index);
        const trk = currentPlaylist.tracks.find(t => t.index === idx);
        if (trk) {
          trk.selected = e.target.checked;
        }
        updateSelectionCounts();
      });
    });

    // Preview play click
    document.querySelectorAll(".thumb-wrapper").forEach(wrap => {
      wrap.addEventListener("click", () => {
        const idx = parseInt(wrap.dataset.index);
        const trk = currentPlaylist.tracks.find(t => t.index === idx);
        if (trk) {
          playAudioPreview(trk);
        }
      });
    });
  }

  // Master Select All / Deselect All
  selectAllCheckbox.addEventListener("change", (e) => {
    const isChecked = e.target.checked;
    if (currentPlaylist && currentPlaylist.tracks) {
      currentPlaylist.tracks.forEach(t => t.selected = isChecked);
      document.querySelectorAll(".track-checkbox").forEach(cb => cb.checked = isChecked);
      updateSelectionCounts();
    }
  });

  function updateSelectionCounts() {
    if (!currentPlaylist || !currentPlaylist.tracks) return;
    const selectedCount = currentPlaylist.tracks.filter(t => t.selected).length;
    const totalCount = currentPlaylist.tracks.length;

    selectedCountBadge.style.display = "inline-block";
    selectedCountBadge.textContent = `${selectedCount} / ${totalCount} Selected`;
    startDownloadBtnText.textContent = `Start Download (${selectedCount} Selected)`;

    selectAllCheckbox.checked = (selectedCount === totalCount);
    btnStartDownload.disabled = (selectedCount === 0);
  }

  // Audio Preview Handling
  async function playAudioPreview(track) {
    if (currentPreviewVideoId === track.id && !audioElement.paused) {
      audioElement.pause();
      updatePlayerPlayIcon(false);
      return;
    }

    currentPreviewVideoId = track.id;
    playerThumb.src = track.thumbnail || "";
    playerTitle.textContent = track.title;
    playerArtist.textContent = track.artist;
    audioPlayerBar.classList.add("active");

    showToast(`Loading preview for "${track.title}"...`, "info");

    try {
      const res = await api.getAudioPreview(track.id, selectedCookies);
      if (res && res.success && res.stream_url) {
        audioElement.src = res.stream_url;
        audioElement.volume = parseFloat(volumeSlider.value);
        audioElement.play();
        updatePlayerPlayIcon(true);
      } else {
        showToast("Could not load preview stream.", "error");
      }
    } catch (e) {
      showToast("Error loading audio preview.", "error");
    }
  }

  btnPlayPause.addEventListener("click", () => {
    if (audioElement.paused) {
      audioElement.play();
      updatePlayerPlayIcon(true);
    } else {
      audioElement.pause();
      updatePlayerPlayIcon(false);
    }
  });

  function updatePlayerPlayIcon(isPlaying) {
    playIcon.style.display = isPlaying ? "none" : "block";
    pauseIcon.style.display = isPlaying ? "block" : "none";
  }

  audioElement.addEventListener("timeupdate", () => {
    if (!isNaN(audioElement.duration)) {
      const current = audioElement.currentTime;
      const duration = audioElement.duration;
      playerCurrentTime.textContent = formatSec(current);
      playerDuration.textContent = formatSec(duration);
      playerSeek.value = (current / duration) * 100;
    }
  });

  playerSeek.addEventListener("input", (e) => {
    if (!isNaN(audioElement.duration)) {
      audioElement.currentTime = (e.target.value / 100) * audioElement.duration;
    }
  });

  volumeSlider.addEventListener("input", (e) => {
    audioElement.volume = parseFloat(e.target.value);
  });

  btnClosePlayer.addEventListener("click", () => {
    audioElement.pause();
    audioElement.src = "";
    audioPlayerBar.classList.remove("active");
    currentPreviewVideoId = null;
  });

  function formatSec(sec) {
    if (isNaN(sec)) return "0:00";
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, "0")}`;
  }

  // Tab Switching
  function switchTab(tabName) {
    tabBtnNewPlaylist.classList.toggle("active", tabName === "new");
    tabBtnDownloads.classList.toggle("active", tabName === "downloads");
    if (tabBtnAbout) tabBtnAbout.classList.toggle("active", tabName === "about");

    viewNewPlaylist.style.display = tabName === "new" ? "flex" : "none";
    viewDownloads.style.display = tabName === "downloads" ? "flex" : "none";
    if (viewAbout) viewAbout.style.display = tabName === "about" ? "flex" : "none";
  }

  tabBtnNewPlaylist.addEventListener("click", () => switchTab("new"));
  tabBtnDownloads.addEventListener("click", () => switchTab("downloads"));
  if (tabBtnAbout) tabBtnAbout.addEventListener("click", () => switchTab("about"));

  // About Us Links
  const setupAboutLink = (elementId, url) => {
    const el = document.getElementById(elementId);
    if (el) {
      el.addEventListener("click", (e) => {
        e.preventDefault();
        api.openUrl(url);
      });
    }
  };

  setupAboutLink("btnOpenWebsite", "https://justrise.bh");
  setupAboutLink("btnLaunchWebsite", "https://justrise.bh");
  setupAboutLink("btnOpenEmail", "mailto:info@justrise.bh");
  setupAboutLink("btnLaunchEmail", "mailto:info@justrise.bh");
  setupAboutLink("btnOpenPhone", "tel:+97333051719");
  setupAboutLink("btnLaunchPhone", "https://wa.me/97333051719");

  window.openJobFolder = function (encodedFolder) {
    const folder = decodeURIComponent(encodedFolder);
    if (folder) {
      api.openFolder(folder);
    }
  };

  function renderDownloadJobs() {
    if (!downloadJobsList) return;
    const activeCount = downloadJobs.filter(j => j.status === "downloading").length;
    if (activeDownloadsBadge) {
      if (activeCount > 0) {
        activeDownloadsBadge.textContent = activeCount;
        activeDownloadsBadge.style.display = "inline-block";
      } else {
        activeDownloadsBadge.style.display = "none";
      }
    }
    if (jobsCountBadge) {
      jobsCountBadge.textContent = `${downloadJobs.length} ${downloadJobs.length === 1 ? "Batch" : "Batches"}`;
    }

    if (downloadJobs.length === 0) {
      downloadJobsList.innerHTML = `
        <div class="empty-jobs-state" id="emptyJobsState">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          <p>No active downloads yet.<br>Analyze a playlist and click <strong>"Start Download"</strong> to send it here!</p>
        </div>
      `;
      return;
    }

    downloadJobsList.innerHTML = downloadJobs.map(job => `
      <div class="download-job-card ${job.status === 'downloading' ? 'active-job' : 'completed-job'}" id="jobCard_${job.id}">
        <div class="job-header">
          <div class="job-title-group">
            <span class="job-title">${escapeHtml(job.playlist_title)}</span>
            <span class="job-badge ${job.status}">${job.status === 'downloading' ? 'Downloading (5x Turbo)' : 'Completed'}</span>
          </div>
          <div class="job-actions">
            ${job.target_dir ? `
              <button class="btn-change-path" onclick="openJobFolder('${encodeURIComponent(job.target_dir)}')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>Open in Finder</span>
              </button>
            ` : ''}
          </div>
        </div>
        <div class="job-progress-wrapper">
          <div class="job-progress-bar">
            <div class="job-progress-fill" id="jobFill_${job.id}" style="width: ${job.percent}%"></div>
          </div>
          <div class="job-meta-row">
            <span id="jobStatusText_${job.id}">${job.completedCount} / ${job.totalTracks} Tracks Completed</span>
            <span id="jobPercentText_${job.id}">${Math.round(job.percent)}%</span>
          </div>
        </div>
      </div>
    `).join("");
  }

  // Start Parallel Download
  btnStartDownload.addEventListener("click", async () => {
    if (!currentPlaylist || !currentPlaylist.tracks) {
      showToast("Please analyze a playlist first.", "error");
      return;
    }

    const selectedTracks = currentPlaylist.tracks.filter(t => t.selected);
    if (selectedTracks.length === 0) {
      showToast("Please select at least 1 track to download.", "error");
      return;
    }

    const playlistTitle = currentPlaylist.playlist_title;
    const newJob = {
      id: "job_" + Date.now(),
      playlist_title: playlistTitle,
      totalTracks: selectedTracks.length,
      completedCount: 0,
      percent: 0,
      status: "downloading",
      target_dir: ""
    };

    downloadJobs.unshift(newJob);
    currentActiveJob = newJob;
    renderDownloadJobs();

    for (let w = 1; w <= 5; w++) {
      resetWorkerUI(w);
    }
    overallProgressText.textContent = `Active: 0 / ${selectedTracks.length} Completed`;

    showToast(`⚡ "${playlistTitle}" moved to Active Downloads queue!`, "success");

    const payload = {
      tracks: selectedTracks,
      playlist_title: playlistTitle,
      base_dir: currentConfig.default_save_path,
      audio_format: selectedFormat,
      browser_cookies: selectedCookies,
      max_workers: 5
    };

    // Cleanly clear the New Playlist screen so user can immediately search/analyze another
    resetNewPlaylistScreen();

    try {
      const res = await api.startDownload(payload);
      if (res && res.target_dir) {
        newJob.target_dir = res.target_dir;
        renderDownloadJobs();
      }
    } catch (e) {
      showToast("Failed to start download.", "error");
      newJob.status = "failed";
      renderDownloadJobs();
    }
  });

  // Reset / New Playlist Input
  btnReset.addEventListener("click", () => {
    resetNewPlaylistScreen();
    showToast("Ready for new playlist!", "info");
    playlistUrlInput.focus();
  });

  function resetNewPlaylistScreen() {
    currentPlaylist = null;
    playlistUrlInput.value = "";
    overviewCard.style.display = "none";
    trackTableBody.innerHTML = "";
    emptyState.style.display = "flex";
    emptyState.innerHTML = `
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 18V5l12-2v13"></path>
        <circle cx="6" cy="18" r="3"></circle>
        <circle cx="18" cy="16" r="3"></circle>
      </svg>
      <p>Paste a YouTube Playlist URL above and click <strong>"Analyze Playlist"</strong> to begin.</p>
    `;

    trackCountBadge.textContent = "0 Tracks";
    selectedCountBadge.style.display = "none";
    tableSearch.value = "";
  }

  function handleWorkerProgress(data) {
    const wid = data.worker_id;
    const trackTitle = data.track_title;
    const percent = data.percent || 0;
    const speedStr = data.speed_str || "";
    const status = data.status || "Downloading";

    if (wid >= 1 && wid <= 5) {
      const fill = document.getElementById(`workerFill${wid}`);
      const label = document.getElementById(`workerLabel${wid}`);
      const trackEl = document.getElementById(`workerTrack${wid}`);
      const speedEl = document.getElementById(`workerSpeed${wid}`);

      if (fill) fill.style.width = `${percent}%`;
      if (label) label.textContent = `${Math.round(percent)}%`;
      if (trackEl) trackEl.textContent = trackTitle;
      if (speedEl) speedEl.textContent = `${speedStr}`;
    }

    if (status === "Downloaded" && currentActiveJob) {
      currentActiveJob.completedCount++;
      currentActiveJob.percent = (currentActiveJob.completedCount / currentActiveJob.totalTracks) * 100;
      
      const jobFill = document.getElementById(`jobFill_${currentActiveJob.id}`);
      const jobStatus = document.getElementById(`jobStatusText_${currentActiveJob.id}`);
      const jobPercent = document.getElementById(`jobPercentText_${currentActiveJob.id}`);
      
      if (jobFill) jobFill.style.width = `${currentActiveJob.percent}%`;
      if (jobStatus) jobStatus.textContent = `${currentActiveJob.completedCount} / ${currentActiveJob.totalTracks} Tracks Completed`;
      if (jobPercent) jobPercent.textContent = `${Math.round(currentActiveJob.percent)}%`;
      
      overallProgressText.textContent = `Active Job: ${currentActiveJob.completedCount} / ${currentActiveJob.totalTracks} Completed`;
    }
  }

  function handleDownloadComplete(data) {
    if (currentActiveJob) {
      currentActiveJob.status = "completed";
      currentActiveJob.completedCount = currentActiveJob.totalTracks;
      currentActiveJob.percent = 100;
      if (data && data.target_dir) {
        currentActiveJob.target_dir = data.target_dir;
      }
      renderDownloadJobs();
      showToast(`✅ "${currentActiveJob.playlist_title}" downloaded successfully!`, "success");
    }

    overallProgressText.textContent = `All active jobs completed!`;

    for (let w = 1; w <= 5; w++) {
      const fill = document.getElementById(`workerFill${w}`);
      const label = document.getElementById(`workerLabel${w}`);
      const trackEl = document.getElementById(`workerTrack${w}`);
      const speedEl = document.getElementById(`workerSpeed${w}`);
      if (fill) fill.style.width = "100%";
      if (label) label.textContent = "100%";
      if (trackEl) trackEl.textContent = "Finished";
      if (speedEl) speedEl.textContent = "Done";
    }
  }

  function resetWorkerUI(wid) {
    const fill = document.getElementById(`workerFill${wid}`);
    const label = document.getElementById(`workerLabel${wid}`);
    const trackEl = document.getElementById(`workerTrack${wid}`);
    const speedEl = document.getElementById(`workerSpeed${wid}`);
    if (fill) fill.style.width = "0%";
    if (label) label.textContent = "0%";
    if (trackEl) trackEl.textContent = "Starting...";
    if (speedEl) speedEl.textContent = "--";
  }

  tableSearch.addEventListener("input", (e) => {
    const term = e.target.value.toLowerCase();
    const rows = trackTableBody.querySelectorAll("tr");
    let visibleCount = 0;
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      if (text.includes(term)) {
        row.style.display = "";
        visibleCount++;
      } else {
        row.style.display = "none";
      }
    });
    trackCountBadge.textContent = `${visibleCount} Tracks`;
  });

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  initConfig();
  renderDownloadJobs();
});

