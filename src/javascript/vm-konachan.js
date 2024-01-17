// ==UserScript==
// @name         Konachan Post
// @version      1.1
// @match        https://konachan.com/post/show/*
// @grant        GM_download
// @grant        GM_xmlhttpRequest
// ==/UserScript==

var retryInterval = 25000;

var maxRetry = 2;
var ifExist = true
var imageData = [];
var failedData = [];
var currentDownloadIndex = 0;
var currentRetry = 0;

var progressElement = document.createElement("progress");
var progressMessage = document.createElement("span");
var tipHint1 = document.createElement('li');
var startTime;


(function () {
    downloadTips();
    try {
      getImageLink();
      downloadImage();
    }

    catch(err) {
      console.log(`%c${err.message}`, "color: red");
      setTips('Image not exist!')
    }
})()


function getImageLink() {
  var elements = document.querySelector("#post-view > script")
  var innerText = elements.textContent
  const regex = /(^\sPost.register_resp\()|(\);\s$)/g
  var res = innerText.replace(regex, '')
  var obj = JSON.parse(res)
  var imgLink = obj.posts[0].file_url
  var imgName = decodeURI(imgLink).split('/').slice(-1)[0]
  // console.log(imgName, imgLink)
  imageData.push({
        name: imgName,
        link: imgLink
    });
  if (!innerText) {
    ifExist = false
  }
}

function downloadImage() {
    if (!imageData.length) {
        console.log('Image not exist...');
        return
    }
    // console.log(imageData[0].link, imageData[0].name);
    var arg = {
        url: imageData[0].link,
        name: imageData[0].name,
        saveAs: false,
        onerror: onError,
        onload: onLoad,
        onprogress: onProgress,
        ontimeout: onTimeout
    };
    startTime = new Date();
    GM_download(arg);
}

function retry() {
    currentRetry++;
    if (currentRetry <= maxRetry) {
        console.log("Retry! " + currentRetry);
        setTimeout(downloadImage, retryInterval);
    } else {
        failedData.push({
            name: imageData[0].name,
            link: imageData[0].link
        })
    }
}

function downloadTips() {
    var logList = [];
    progressElement.value = 0;
    progressElement.max = 100;
    progressElement.id = 'tipsProgressBar';
    progressMessage.id = 'tipsProgress';
    const arr = ["Downloading...", "", "Complete!"];
    const div = document.createElement('div');
    const ul = document.createElement("ul");

    tipHint1.classList.add('progress');
    tipHint1.id = 'tip1';
    tipHint1.innerHTML = arr[0];

    const li1 = document.createElement('li');
    li1.classList.add('result');
    li1.id = 'tip2';
    li1.innerHTML = arr[1];

    ul.appendChild(tipHint1);
    ul.appendChild(progressElement);
    ul.appendChild(progressMessage);
    ul.appendChild(li1);
    // li.setAttribute ('style', 'display: block;');

    div.classList.add('download_tip');
    div.id = ('moe_download');
    ul.setAttribute('style', 'padding: 0; margin: 0;');
    ul.setAttribute('id', 'theList');

    div.appendChild(ul);
    logList.push(div);
    insertToHead(div);
    // const li1 = document.createElement('li');
    // const li0 = document.createElement('li');
    // li0.innerHTML = arr[0];
    // li1.innerHTML = arr[1];
    // ul.appendChild(li0);
    // ul.appendChild(li1);
    // li0.classList.add('progress');
    // li1.classList.add('result');
    // li0.id = 'tip1';
    // li1.id = 'tip2';
    // // li.setAttribute ('style', 'display: block;');
    // div.classList.add('download_tip');
    // div.id = ('moe_download');
    // ul.setAttribute('style', 'padding: 0; margin: 0;');
    // ul.setAttribute('id', 'theList');
    // div.appendChild(ul);
    // logList.push(div);
    // insertToHead(div);
}


function setTips(tips) {
    var result = document.querySelector("#tip2");
    result.innerHTML = tips
}

function insertToHead(ele) {
    document.querySelector("#header").insertAdjacentElement('beforebegin', ele);
    return ele
}

function onLoad() {
    setTips("Complete!");
    console.log("%cDownload Completed!", "color: mediumseagreen");
    // window.stop();
    // console.log("%cStop Loading!", "color: red");
}

function onError(err) {
    console.log("%cError! Reason: " + err.error, "color: crimson");
    retry();
}

function onProgress(progress) {
    console.log("%cDownloading...", "color: chartreuse");
    progressElement.value = (progress.loaded / progress.total) * 100;
    var loadedMB = (progress.loaded / (1024 * 1024)).toFixed(2);
    var totalMB = (progress.total / (1024 * 1024)).toFixed(2);
    var elapsed =  (new Date() - startTime) / 1000;
    var speed = progress.loaded / 1024 / elapsed;
    var speedShow;
    if (speed > 1024) {
      speedShow = `${(speed / 1024).toFixed(2)}mib/s`
    }
    else {
      speedShow = `${speed.toFixed(2)}kib/s`
    }
    progressMessage.innerHTML = `   ${speedShow}`
    tipHint1.innerHTML = `Downloading...  ${loadedMB}MB/${totalMB}MB`;
}

function onTimeout() {
    console.log("%cTimeout!", "color: brown");
    retry();
}


