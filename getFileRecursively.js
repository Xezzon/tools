const fs = require('fs');
const path = require('path');

function getFile(targetPath) {
    let filelist = [];
    let dir = fs.readdirSync(targetPath).filter((filename) => filename.indexOf('.') !== 0);
    dir.forEach((dirname) => {
        let filepath = path.join(targetPath, dirname);
        if (fs.lstatSync(filepath).isFile()) {
            filelist.push(filepath);
        } else {
            filelist.push(...getFile(filepath));
        }
    });
    return filelist;
}

let filelist = getFile(__dirname);
console.debug(filelist);
