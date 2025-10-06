
const dispatch = (task, list) => { 
    return backend?.dispatch(task, list) ?? -1; 
}

const getResult = (id) => { 
    return backend?.get_result(id) ?? "";
}

const readFile = (filePath) => {
    return new Promise((resolve, reject) => {
        const request = new XMLHttpRequest();
        request.open('GET', Qt.resolvedUrl(filePath), false);
        request.send(null);
        if (request.status === 200) {
            resolve(request.responseText);
        } else {
            reject(new Error(`Failed to load ${filePath}: ${request.statusText}`));
        }
    });
};