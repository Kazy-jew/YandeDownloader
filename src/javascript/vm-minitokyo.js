// ==UserScript==
// @name        minitokyo.net Downloader
// @namespace   nil
// @match       http://gallery.minitokyo.net/view/*
// @grant       GM_download
// @version     1.0
// @author      decipherer
// @description 5/7/2023, 1:28:45 AM
// ==/UserScript==


var retryInterval = 25000;
var maxRetry = 2;
var imgData = {};
var lastId;
var lastExistId;

var currentRetry = 0;
var startTime;
var progressElement = document.createElement("progress");
var progressMessage = document.createElement("span");
var tipHint1 = document.createElement('li');

(function () {
  console.log(`%cbegin here`, "color: green");
  var result = checkExists();
  if (result == -1) {
    getImageTags();
    getImageInfo();
    getImageLink();
    downloadTips();
    downloadImage();
  } else {
    const endHint = document.createElement("div");
    endHint.id = "tip2";
    result == 0 ? endHint.textContent = "END!" : endHint.textContent = "Deleted!";
    // Insert the new element into the page
    const targetElement = document.querySelector("#content");
    targetElement.appendChild(endHint);
    console.log(`%cend of world here`, "color: crimson")
  }
})()

function checkExists() {
  const currentURL = window.location.href;
  var currentId = currentURL.substring(currentURL.lastIndexOf("/") + 1);
  console.log(`${currentURL}, currentId: ${currentId}`)

  var existence = document.querySelector("head > title")

  // test code
  // if (currentId == 757950) { return false}
  if (existence.textContent.includes('Not Found')) {
    console.log(`%c${existence.textContent}`, "color: crimson")
      lastId = lastExistId;
      return 0
      } else if  (existence.textContent.includes('Deleted')) {
        return 1
      }
   else {
    lastExistId = currentId;
    lastId = null;
    return -1
  }
}

function getImageTags() {
  var elements = document.querySelector("#tag-list > ul");
  var liElements = elements.querySelectorAll('li');
  var imgTags = {};

  for (var i = 0; i < liElements.length; i++) {
		var liElement = liElements[i];
    var tagText;
    var tagProperty;
    var em = liElement.querySelector('em');
    if (em) {
      tagText = em.querySelector('a').textContent.trim()
      tagProperty = liElement.querySelector('b').textContent.trim()
    } else {
      tagText = liElement.querySelector('a').textContent.trim()
      tagProperty = "general"
    }
    imgTags[tagText] = tagProperty
    // console.log(`%c${tagText} ${tagProperty}`, "color: blue")
  }
  console.log(`%c${JSON.stringify(imgTags)}`, "color: blue");
  imgData.imgTags = imgTags

  var keys = Object.keys(imgTags).map(key => key.replace(/\s+/g, '_'));
  imgData.tags = keys.join(' ');
}


function getImageInfo() {
  var elements = document.querySelector("#menu > dl");
  var dtElements = elements.querySelectorAll('dt');
  var ddElements = elements.querySelectorAll('dd');
  var imgInfo = {};

  // var dtArray = [];
  // var ddArray = [];
  // dtElements.forEach(dtElement => dtArray.push(dtElement.textContent))
  // ddElements.forEach(ddElement => ddArray.push(ddElement.textContent))
  // console.log(`%c${dtArray}`, "color: green")
  // console.log(`%c${ddArray}`, "color: green")

  for (var i = 0; i < dtElements.length; i++) {
		var dtElement = dtElements[i];
    var ddElement = ddElements[i];
    var text = dtElement.textContent.trim();
    if (text == 'Timestamp') {
      let timeStamp = ddElement.querySelector('span').getAttribute('title');
      timeStamp ? imgInfo[text] = timeStamp : imgInfo[text] = ddElement.querySelector('span').textContent.trim()
    } else {
      imgInfo[text] = ddElement.textContent.trim();
    }
  }
  console.log(`%c${JSON.stringify(imgInfo)}`, "color: DarkOliveGreen");
  imgData.imgInfo = imgInfo

}


function getImageLink() {
  var preview = document.querySelector("#preview > a > img").getAttribute('src');
  var imgLink = "http://static.minitokyo.net/downloads" + preview.split('view')[1];
  var imgId = preview.split('/').pop().split('.')[0];
  var imgType = preview.split(imgId).pop();
  console.log(`%c${imgLink}, ${imgId}`, "color: Indigo");
  imgData.link = imgLink;
  imgData.id = imgId;
  imgData.format = imgType;

  imgData.imgInfo.id = imgId;
  imgData.imgInfo.link = imgLink;
  imgData.imgInfo.ext = imgType
}


function downloadImage() {
  if (!imgData.link) {
      console.log('%cImage not exist...', "color: crimson");
      return
  }
  let name = 'minitokyo.net ' + imgData.id + ' ' + imgData.tags + imgData.format
  console.log(`%c${name}`, "color: Orchid")
  var arg = {
      url: imgData.link,
      name: name,
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
            name: imgData.id,
            link: imgData.link
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
  const imgInfoUl = document.createElement("ul");
  const imgTagUl = document.createElement("ul");
  const li1 = document.createElement('li');

  tipHint1.classList.add('progress');
  tipHint1.id = 'tip2';
  tipHint1.innerHTML = arr[0];

  ul.appendChild(tipHint1);
  li1.appendChild(progressElement);
  li1.appendChild(progressMessage);
  ul.appendChild(li1);
  // li.setAttribute ('style', 'display: block;');
  li1.setAttribute('style', 'margin: auto 0; text-align: left; max-width: 50%;');

  div.classList.add('download_tip');
  div.id = ('moe_download');
  div.setAttribute('style', 'margin: 0; padding: 0');
  ul.setAttribute('style', 'text-align: center; display: flex; justify-content: center; align-items: center; flex-direction: column;');
  ul.setAttribute('id', 'theList');

  imgInfoUl.id = 'imageInfo';
  imgInfoUl.innerHTML = `<!-- ${JSON.stringify(imgData.imgInfo)} -->`;
  imgInfoUl.setAttribute('style', 'display: none; visibility: hidden');

  imgTagUl.id = 'imageTags'
  imgTagUl.innerHTML = `<!-- ${JSON.stringify(imgData.imgTags)} -->`;
  imgTagUl.setAttribute('style', 'display: none; visibility: hidden');

  div.appendChild(ul);
  div.appendChild(imgInfoUl);
  div.appendChild(imgTagUl);

  logList.push(div);
  insertToHead(div);
}


function setTips(tips) {
    var result = document.querySelector("#tip2");
    result.innerHTML = result.innerHTML.replace('Downloading...', `${tips} `)
}


function insertToHead(ele) {
    document.querySelector("#preview").insertAdjacentElement('beforebegin', ele);
    return ele
}


function onLoad() {
    setTips("Complete!");
    console.log("%cDownload Completed!", "color: mediumseagreen");
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
    speed > 1024 ? speedShow = `${(speed / 1024).toFixed(2)}mib/s` : speedShow = `${speed.toFixed(2)}kib/s`
    progressMessage.innerHTML = `   ${speedShow}`
    tipHint1.innerHTML = `Downloading...  ${loadedMB}MB/${totalMB}MB`;
}

function onTimeout() {
    console.log("%cTimeout!", "color: brown");
    retry();
}