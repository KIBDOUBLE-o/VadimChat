
// source:script_main

const debugPanel = document.getElementById("debugPanel");
const toggleDebugBtn = document.getElementById("toggleDebugBtn");
const closeDebugBtn = document.getElementById("closeDebugBtn");
const debugMessages = document.getElementById("debugMessages");
const debugInput = document.getElementById("debugInput");
const debugSendBtn = document.getElementById("debugSendBtn");

const pluginsTopBtn = document.getElementById("pluginsTopBtn");
const serversTopBtn = document.getElementById("serversTopBtn");

disableDebug();

toggleDebugBtn.onclick = () => {
    debugPanel.style.display = (debugPanel.style.display === "flex") ? "none" : "flex";
};

function setVersion(version) {
    const versionText = document.getElementById("versionText");
    if (versionText) {
        versionText.textContent = "v" + version;
    }
}

closeDebugBtn.onclick = () => {
    debugPanel.style.display = "none";
};

function disableDebug() {
    toggleDebugBtn.style.display = "none";
}

function enableDebug() {
    toggleDebugBtn.style.display = "flex";
}

function logDebug(message, type = "info") {
    const div = document.createElement("div");
    div.classList.add("debug-line");
    div.classList.add(type);
    div.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    debugMessages.appendChild(div);
    debugMessages.scrollTop = debugMessages.scrollHeight;
}

debugSendBtn.onclick = () => {
    const val = debugInput.value.trim();
    if (!val) return;
    logDebug(`> ${val}`, "command");
    debugInput.value = "";
};


const menu = document.getElementById("menu");
const chat = document.getElementById("chat");
const inputbar = document.getElementById("inputbar");
const joinForm = document.getElementById("joinForm");
const createBtn = document.getElementById("createBtn");
const joinBtn = document.getElementById("joinBtn");
const connectBtn = document.getElementById("connectBtn");
const reconnectBtn = document.getElementById("reconnectBtn");
const minimizeBtn = document.getElementById("minimizeBtn");

createBtn.onclick = () => startChat("server");
joinBtn.onclick = () => {
    createBtn.style.display = "none";
    joinBtn.style.display = "none";
    reconnectBtn.style.display = "none";
    joinForm.style.display = "flex";
};
connectBtn.onclick = () => {
    joinForm.style.display = "none";
    const key = document.getElementById("joinKey").value.trim();
    const name = document.getElementById("joinName").value.trim();
    if (key && name) startChat("client", { key, name });
};
reconnectBtn.onclick = () => {
    window.pywebview.api.reconnect();

    menu.style.display = "none";
    chat.style.display = "block";
    inputbar.style.display = "block";
};

minimizeBtn.onclick = () => {
    window.pywebview.api.minimize();
};

function startChat(mode, data = {}) {
    menu.style.display = "none";
    chat.style.display = "block";
    inputbar.style.display = "block";

    if (mode === "server") {
        window.pywebview.api.create_chat();
        addMessage("Вы создали чат. Ожидание подключений...", "server");
    } else if (mode === "client") {
        window.pywebview.api.join_chat(data.key, data.name);
        addMessage(`Подключение к чату с ключом ${data.key}...`, "server");
    }
}

function setNickName(name) {
    document.getElementById("joinName").value = name;
}

function closeChat() {
    menu.style.display = "flex";
    chat.style.display = "none";
    inputbar.style.display = "none";
    createBtn.style.display = "";
    joinBtn.style.display = "";
    joinForm.style.display = "none";
    reconnectBtn.style.display = "block";
}

function exitChat() {
    clearMessages();
    closeChat();
    window.pywebview.api.exit_chat()
}

function scrollToBottom() {
    const messages = document.getElementById("messages");
    messages.scrollTop = messages.scrollHeight;
}

function addMessage(text, sender, name="") {
    const wrap = document.createElement("div");
    wrap.className = "message";

    const nameDiv = document.createElement("div");
    nameDiv.className = "name";

    const bubble = document.createElement("div");

    if(sender === "me") {
        nameDiv.style.textAlign = "right";
        nameDiv.textContent = name || "Я";
        bubble.className = "bubble-me";
    }
    else if(sender === "server") {
        nameDiv.style.textAlign = "center";
        nameDiv.textContent = name || "Сервер";
        bubble.className = "bubble-server";
    }
    else {
        nameDiv.style.textAlign = "left";
        nameDiv.textContent = name || "Игрок";
        bubble.className = "bubble-other";
    }

    bubble.textContent = text;
    wrap.appendChild(nameDiv);
    wrap.appendChild(bubble);
    document.getElementById("messages").appendChild(wrap);

    setTimeout(scrollToBottom, 200);
}

function acceptMessage() {
    const inp = document.getElementById("msg");
    const val = inp.value.trim();
    if(val) {
        window.pywebview.api.send_message(val);
        inp.value = "";
    }
}
document.getElementById("msg").addEventListener("keypress", e => {
    if(e.key === "Enter") acceptMessage();
});

function clearMessages() {
    const messages = document.getElementById("messages");
    messages.innerHTML = "";
}



document.addEventListener("dragover", e => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
});

document.addEventListener("drop", e => {
    e.preventDefault();
    if (e.dataTransfer.files.length > 0) {
        for (let file of e.dataTransfer.files) {
            const reader = new FileReader();
            reader.onload = evt => {
                const base64 = evt.target.result.split(",")[1]; // убираем data:...;base64,
                const fileData = {
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    data: base64
                };
                window.pywebview.api.send_file(fileData);

                addFileMessage(evt.target.result, "me", file.name, "Я");
            };
            reader.readAsDataURL(file);
        }
    }
});

function addFileMessage(src, sender, file_name, name = "") {
    const wrap = document.createElement("div");
    wrap.className = "message";

    const nameDiv = document.createElement("div");
    nameDiv.className = "name";

    const bubble = document.createElement("div");
    bubble.className =
        sender === "me" ? "bubble-me" :
        sender === "server" ? "bubble-server" : "bubble-other";

    nameDiv.style.textAlign =
        sender === "me" ? "right" :
        sender === "server" ? "center" : "left";

    nameDiv.textContent =
        sender === "me" ? (name || "Я") :
        sender === "server" ? (name || "Сервер") :
        (name || "Игрок");

    const isImage =
        typeof src === "string" &&
        (src.startsWith("data:image/") ||
         /\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i.test(src));

    const img = document.createElement("img");
    img.src = src;
    img.alt = file_name || "Файл";
    img.style.maxWidth = "200px";
    img.style.borderRadius = "12px";
    img.style.cursor = "pointer";
    img.title = isImage ? "Открыть изображение" : "Открыть местоположение файла";

    img.onclick = () => {
        if (isImage) {
            const overlay = document.createElement("div");
            overlay.style.position = "fixed";
            overlay.style.top = 0;
            overlay.style.left = 0;
            overlay.style.width = "100vw";
            overlay.style.height = "100vh";
            overlay.style.background = "rgba(0,0,0,0.8)";
            overlay.style.display = "flex";
            overlay.style.justifyContent = "center";
            overlay.style.alignItems = "center";
            overlay.style.zIndex = 9999;
            overlay.onclick = () => overlay.remove();

            const fullImg = document.createElement("img");
            fullImg.src = src;
            fullImg.style.maxWidth = "90%";
            fullImg.style.maxHeight = "90%";
            fullImg.style.borderRadius = "12px";
            fullImg.style.boxShadow = "0 0 20px rgba(0,0,0,0.5)";
            overlay.appendChild(fullImg);
            document.body.appendChild(overlay);
        } else {
            window.pywebview.api.open_shared_folder("data/shared_assets");
        }
    };

    bubble.appendChild(img);
    wrap.appendChild(nameDiv);
    wrap.appendChild(bubble);
    document.getElementById("messages").appendChild(wrap);

    setTimeout(scrollToBottom, 200);
}



const settingsBtn = document.getElementById("settingsBtn");
const settingsMenu = document.getElementById("settingsMenu");
const closeSettingsBtn = document.getElementById("closeSettingsBtn");
const basicTab = document.getElementById("basicTab");
const advancedTab = document.getElementById("advancedTab");
const basicSettings = document.getElementById("basicSettings");
const advancedSettings = document.getElementById("advancedSettings");
const applySettingsBtn = document.getElementById("applySettingsBtn");

let settings = {};
let settingElements = {};

settingsBtn.onclick = () => settingsMenu.style.display = "block";
closeSettingsBtn.onclick = () => settingsMenu.style.display = "none";

pluginsTopBtn.onclick = () => {
    pluginsMenu.style.display = "block";
    loadPlugins();
};

serversTopBtn.onclick = () => showServersMenu();

function activateTab(tab) {
    if(tab === "basic") {
        basicSettings.style.display = "flex";
        advancedSettings.style.display = "none";
        basicTab.classList.add("active");
        advancedTab.classList.remove("active");
    } else {
        basicSettings.style.display = "none";
        advancedSettings.style.display = "flex";
        basicTab.classList.remove("active");
        advancedTab.classList.add("active");
    }
}
basicTab.onclick = () => activateTab("basic");
advancedTab.onclick = () => activateTab("advanced");

applySettingsBtn.onclick = () => {
    window.pywebview.api.apply_settings(settings);
};

function addSetting(id, title, default_value, type="field", is_adv=false) {
    settings[id] = default_value;

    const createInput = () => {
        const container = document.createElement("div");
        container.className = "window-list-item";
        container.style.cursor = "default";
        container.onclick = null;

        let inputHtml;
        if(type === "toggle") {
            inputHtml = `
                <div class="window-list-item-header">
                    <span class="window-list-item-name">${title}</span>
                    <label class="switch">
                        <input type="checkbox" ${default_value ? 'checked' : ''}>
                        <span class="slider round"></span>
                    </label>
                </div>
            `;
        } else {
            inputHtml = `
                <div class="window-list-item-header">
                    <span class="window-list-item-name">${title}</span>
                </div>
                <input type="text" value="${default_value}" 
                       style="width: 100%; margin-top: 10px; padding: 8px; 
                              background: rgba(255,255,255,0.05); 
                              border: 1px solid rgba(255,255,255,0.1); 
                              border-radius: 6px; color: white;">
            `;
        }

        container.innerHTML = inputHtml;
        
        const input = container.querySelector(type === "toggle" ? "input[type='checkbox']" : "input[type='text']");
        
        if (type === "toggle") {
            input.onchange = () => {
                settings[id] = input.checked;
                if(settingElements[id] && settingElements[id][1] && settingElements[id][1] !== input) {
                    settingElements[id][1].checked = input.checked;
                }
            };
        } else {
            input.oninput = () => {
                settings[id] = input.value;
                if(settingElements[id] && settingElements[id][1] && settingElements[id][1] !== input) {
                    settingElements[id][1].value = input.value;
                }
            };
        }
        
        input.style.flex = "1 1 auto";
        input.style.background = "rgba(60, 63, 65, 0.5)";
        input.style.color = "white";
        input.style.border = "1px solid rgba(255, 255, 255, 0.1)";
        input.style.borderRadius = "6px";
        input.style.padding = "8px 12px";

        return { container, input };
    };

    const { container, input } = createInput();
    let inputs = [input];

    if(is_adv) {
        advancedSettings.appendChild(container);
    } else {
        basicSettings.appendChild(container);
        const advContainer = container.cloneNode(true);
        advancedSettings.appendChild(advContainer);
        const advInput = advContainer.querySelector(type === "toggle" ? "input[type='checkbox']" : "input[type='text']");
        inputs.push(advInput);

        if(type === "toggle") {
            advInput.onchange = input.onchange;
        } else {
            advInput.oninput = input.oninput;
        }
    }

    settingElements[id] = inputs;
}

function setSetting(id, value) {
    if(settingElements[id]) {
        for(const el of settingElements[id]) {
            if(el.type === "checkbox") el.checked = value;
            else el.value = value;
        }
        settings[id] = value;
    }
}

addSetting("default_ip", "Стандартный IP", "127.0.0.1", "field", false);
addSetting("use_universal", "Использовать универсальный IP", true, "toggle", false);
addSetting("port", "Порт", "12345", "field", false);

addSetting("universal", "Универсальный IP", "0.0.0.0", "field", true);
addSetting("buffer_size", "Размер Буффера", "4096", "field", true);
addSetting("data_chunk_size", "Размер Куска Данных", "1024", "field", true);
addSetting("chunk_sending_rate", "Частота Отправки Кусков", "0.05", "field", true);
addSetting("debug_mode", "Режим Отладки", false, "toggle", true);

activateTab("basic");






const pluginsMenu = document.getElementById("pluginsMenu");
const closePluginsBtn = document.getElementById("closePluginsBtn");
const pluginsList = document.getElementById("pluginsList");
const refreshPluginsBtn = document.getElementById("refreshPluginsBtn");
const pluginsTabActive = document.getElementById("pluginsTabActive");
const pluginsTabAll = document.getElementById("pluginsTabAll");
const pluginsTabStore = document.getElementById("pluginsTabStore");

let plugins = {};
let currentPluginsTab = "active";

closePluginsBtn.onclick = () => {
    pluginsMenu.style.display = "none";
};

refreshPluginsBtn.onclick = () => {
    loadPlugins();
};

pluginsTabActive.onclick = () => activatePluginsTab("active");
pluginsTabAll.onclick = () => activatePluginsTab("all");
pluginsTabStore.onclick = () => activatePluginsTab("store");

function activatePluginsTab(tab) {
    currentPluginsTab = tab;
    pluginsTabActive.classList.toggle("active", tab === "active");
    pluginsTabAll.classList.toggle("active", tab === "all");
    pluginsTabStore.classList.toggle("active", tab === "store");
    renderPluginsList();
}

function addPlugin(pluginData) {
    const pluginId = pluginData.id || `plugin_${Date.now()}`;

    plugins[pluginId] = {
        id: pluginId,
        display_name: pluginData.display_name || "Без названия",
        description: pluginData.description || "Описание отсутствует",
        version: pluginData.version || "1.0.0",
        author: pluginData.author || "Неизвестный автор",
        enabled: pluginData.enabled !== undefined ? pluginData.enabled : true,
        settings: pluginData.settings || [],
        onEnable: pluginData.onEnable,
        onDisable: pluginData.onDisable,
        onSettings: pluginData.onSettings
    };

    if (plugins[pluginId].enabled && plugins[pluginId].onEnable) {
        try {
            plugins[pluginId].onEnable();
        } catch (error) {
            console.error(`Ошибка при включении плагина ${pluginId}:`, error);
        }
    }

    if (pluginsMenu.style.display === "block") {
        renderPluginsList();
    }

    logDebug("Plugin added");
    return pluginId;
}

function loadPlugins() {
    renderPluginsList();
}

function renderPluginsList() {
    pluginsList.innerHTML = "";

    const pluginsArray = Object.values(plugins);

    let filteredPlugins = pluginsArray;
    if (currentPluginsTab === "active") {
        filteredPlugins = pluginsArray.filter(p => p.enabled);
    } else if (currentPluginsTab === "store") {
        pluginsList.innerHTML = `
            <div class="window-empty-state">
                <div style="font-size: 48px; margin-bottom: 20px;">🛒</div>
                <h3>Магазин плагинов</h3>
                <p style="color: #888; margin-top: 10px;">
                    Функция магазина плагинов в разработке.<br>
                    Скоро здесь можно будет устанавливать новые плагины!
                </p>
            </div>
        `;
        return;
    }

    if (filteredPlugins.length === 0) {
        pluginsList.innerHTML = `
            <div class="window-empty-state">
                <div style="font-size: 48px; margin-bottom: 20px;">
                    ${currentPluginsTab === "active" ? "🔌" : "📁"}
                </div>
                <h3>${currentPluginsTab === "active" ? "Нет активных плагинов" : "Плагины не найдены"}</h3>
                <p style="color: #888; margin-top: 10px;">
                    ${currentPluginsTab === "active" 
                        ? "Включите плагины во вкладке 'Все плагины'" 
                        : "Добавьте плагины через API или магазин"}
                </p>
            </div>
        `;
        return;
    }

    filteredPlugins.forEach(plugin => {
        const pluginElement = document.createElement("div");
        pluginElement.className = "window-list-item";

        pluginElement.innerHTML = `
            <div class="window-list-item-header">
                <span class="window-list-item-name">${plugin.display_name}</span>
                <div class="window-list-item-meta">
                    <span class="window-list-item-version">v${plugin.version}</span>
                    <span class="window-list-item-author">${plugin.author}</span>
                </div>
            </div>
            <div class="window-list-item-description">${plugin.description}</div>
            <div class="window-list-item-controls">
                <button class="window-list-btn ${plugin.enabled ? 'success' : ''}" 
                        onclick="togglePlugin('${plugin.id}')">
                    ${plugin.enabled ? '✅ Включен' : '🔴 Выключен'}
                </button>
                ${plugin.onSettings ? `
                <button class="window-list-btn" onclick="openPluginSettings('${plugin.id}')">
                    ⚙️ Настройки
                </button>
                ` : ''}
                <button class="window-list-btn danger" onclick="removePlugin('${plugin.id}')">
                    🗑 Удалить
                </button>
            </div>
        `;

        pluginsList.appendChild(pluginElement);
    });
}

function togglePlugin(pluginId) {
    if (plugins[pluginId]) {
        plugins[pluginId].enabled = !plugins[pluginId].enabled;

        try {
            if (plugins[pluginId].enabled) {
                if (plugins[pluginId].onEnable) {
                    plugins[pluginId].onEnable();
                }
                logDebug(`Плагин "${plugins[pluginId].display_name}" включен`, "info");
            } else {
                if (plugins[pluginId].onDisable) {
                    plugins[pluginId].onDisable();
                }
                logDebug(`Плагин "${plugins[pluginId].display_name}" отключен`, "info");
            }
        } catch (error) {
            console.error(`Ошибка при переключении плагина ${pluginId}:`, error);
            logDebug(`Ошибка в плагине "${plugins[pluginId].display_name}": ${error.message}`, "error");
        }
        window.pywebview.api.set_plugin_state(pluginId, plugins[pluginId].enabled);
        renderPluginsList();
    }
}

function openPluginSettings(pluginId) {
    if (plugins[pluginId] && plugins[pluginId].onSettings) {
        try {
            plugins[pluginId].onSettings();
        } catch (error) {
            console.error(`Ошибка при открытии настроек плагина ${pluginId}:`, error);
            alert(`Ошибка в настройках плагина: ${error.message}`);
        }
    }
}

function removePlugin(pluginId) {
    if (plugins[pluginId] && confirm(`Удалить плагин "${plugins[pluginId].display_name}"?`)) {
        if (plugins[pluginId].enabled && plugins[pluginId].onDisable) {
            try {
                plugins[pluginId].onDisable();
            } catch (error) {
                console.error(`Ошибка при отключении плагина перед удалением:`, error);
            }
        }

        delete plugins[pluginId];
        renderPluginsList();
        logDebug(`Плагин удален: ${pluginId}`, "info");
    }
}

function getPlugins() {
    return plugins;
}

function getPlugin(pluginId) {
    return plugins[pluginId];
}

activatePluginsTab("active");

function addButtonMessage(text, sender, name = "", id, buttons = []) {
    if (!Array.isArray(buttons) || buttons.length === 0 || buttons.length > 4) {
        console.error("buttons must be array of 1–4 strings");
        return;
    }

    const wrap = document.createElement("div");
    wrap.className = "message";

    const nameDiv = document.createElement("div");
    nameDiv.className = "name";

    const bubble = document.createElement("div");
    bubble.style.display = "flex";
    bubble.style.flexDirection = "column";
    bubble.style.gap = "8px";

    if (sender === "me") {
        nameDiv.style.textAlign = "right";
        nameDiv.textContent = name || "Я";
        bubble.className = "bubble-me";
    } else if (sender === "server") {
        nameDiv.style.textAlign = "center";
        nameDiv.textContent = name || "Сервер";
        bubble.className = "bubble-server";
    } else {
        nameDiv.style.textAlign = "left";
        nameDiv.textContent = name || "Игрок";
        bubble.className = "bubble-other";
    }

    const textDiv = document.createElement("div");
    textDiv.textContent = text;
    bubble.appendChild(textDiv);

    const btnBlock = document.createElement("div");
    btnBlock.style.display = "flex";
    btnBlock.style.flexWrap = "wrap";
    btnBlock.style.gap = "6px";
    btnBlock.style.marginTop = "4px";

    buttons.forEach((label, index) => {
        const btn = document.createElement("button");
        btn.textContent = label;
        btn.style.flex = "1 1 auto";

        btn.onclick = () => {
            try {
                window.pywebview.api.button_pressed(id, index);
            } catch (e) {
                console.error("buttonPressed error:", e);
            }
        };

        btnBlock.appendChild(btn);
    });

    bubble.appendChild(btnBlock);

    wrap.appendChild(nameDiv);
    wrap.appendChild(bubble);

    document.getElementById("messages").appendChild(wrap);
    wrap.scrollIntoView();
}

function sendTable(sender, id, columns, data, name="") {
    const wrap = document.createElement("div");
    wrap.className = "message";

    const nameDiv = document.createElement("div");
    nameDiv.className = "name";

    const bubble = document.createElement("div");
    bubble.style.overflowX = "auto"; 

    if(sender === "me") {
        nameDiv.style.textAlign = "right";
        nameDiv.textContent = name || "Я";
        bubble.className = "bubble-me";
    } else if(sender === "server") {
        nameDiv.style.textAlign = "center";
        nameDiv.textContent = name || "Сервер";
        bubble.className = "bubble-server";
    } else {
        nameDiv.style.textAlign = "left";
        nameDiv.textContent = name || "Игрок";
        bubble.className = "bubble-other";
    }

    const table = document.createElement("table");
    table.style.borderCollapse = "collapse";
    table.style.width = "100%";
    table.style.marginTop = "4px";

    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    columns.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col;
        th.style.border = "1px solid #555";
        th.style.padding = "6px 8px";
        th.style.background = "rgba(255,255,255,0.1)";
        th.style.textAlign = "left";
        headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    data.forEach(row => {
        const tr = document.createElement("tr");
        row.forEach(cell => {
            const td = document.createElement("td");
            td.textContent = cell;
            td.style.border = "1px solid #555";
            td.style.padding = "4px 6px";
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    bubble.appendChild(table);
    wrap.appendChild(nameDiv);
    wrap.appendChild(bubble);
    document.getElementById("messages").appendChild(wrap);

    wrap.scrollIntoView();
}






const serversMenu = document.getElementById("serversMenu");
const closeServersBtn = document.getElementById("closeServersBtn");
const serversList = document.getElementById("serversList");
const clearServersBtn = document.getElementById("clearServersBtn");

let servers = []; 

closeServersBtn.onclick = () => serversMenu.style.display = "none";

clearServersBtn.onclick = () => {
    clearServers();
    renderServersList();
};


function showServersMenu() {
    renderServersList();
    serversMenu.style.display = "block";
}


function addServer(key, name = "Без имени") {
    if (!servers.some(s => s.key === key)) {
        servers.push({ key, name });
    }
    renderServersList();
}



function clearServers() {
    servers = [];
    renderServersList();
}


function setServers(list) {
    servers = Array.from(new Set(list));
    renderServersList();
}


function renderServersList() {
    serversList.innerHTML = "";

    if (servers.length === 0) {
        serversList.innerHTML = `
            <div class="window-empty-state">
                <div style="font-size: 48px; margin-bottom: 20px;">🌐</div>
                <h3>Список пуст</h3>
                <p style="color: #888; margin-top: 10px;">
                    Подключитесь к комнате, чтобы она появилась в списке
                </p>
            </div>`;
        return;
    }

    servers.forEach(server => {
        const item = document.createElement("div");
        item.className = "window-list-item";
        item.onclick = () => selectServer(server);

        item.innerHTML = `
            <div class="window-list-item-header">
                <span class="window-list-item-name">${server.name}</span>
                <div class="window-list-item-meta">
                    <span class="window-list-item-author">${server.key}</span>
                </div>
            </div>
            <div class="window-list-item-description">
                Нажмите для подключения
            </div>
        `;

        serversList.appendChild(item);
    });
}

function selectServer(server) {
    serversMenu.style.display = "none";

    joinForm.style.display = "flex";
    createBtn.style.display = "none";
    joinBtn.style.display = "none";
    reconnectBtn.style.display = "none";

    document.getElementById("joinKey").value = server.key;
}


const refreshServersBtn = document.getElementById("refreshServersBtn");

refreshServersBtn.onclick = async () => {
    await refreshServers();
    renderServersList();
};

async function refreshServers() {
    window.pywebview.api.refresh_servers();
}


const style = document.createElement('style');
style.textContent = `
    .switch {
        position: relative;
        display: inline-block;
        width: 50px;
        height: 24px;
    }
    
    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(255,255,255,0.1);
        transition: .4s;
        border-radius: 24px;
    }
    
    .slider:before {
        position: absolute;
        content: "";
        height: 16px;
        width: 16px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }
    
    input:checked + .slider {
        background: linear-gradient(135deg, #007acc, #005f99);
    }
    
    input:checked + .slider:before {
        transform: translateX(26px);
    }
`;
document.head.appendChild(style);