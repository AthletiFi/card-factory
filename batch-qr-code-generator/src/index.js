const { QRCodeCanvas } = require('@loskir/styled-qr-code-node');
const csv = require('csv-parser');
const fs = require('fs-extra');
const path = require('path');

// Import the QR code options from options.json
const qrCodeOptions = require('./options.json');
  
// Function to generate QR code
async function createQR(url, index, options) {
    options.data = url;
    const qrCode = new QRCodeCanvas({ ...options, data: url });

    try {
        // Ensure the qr_codes directory exists
        await fs.ensureDir('./qr_codes');

        const filePath = `./qr_codes/qr_${index + 1}.svg`;

        // Uncomment this if you want to do PNG instead: 
        // await qrCode.toFile(`./qr_codes/qr_${index + 1}.png`, 'png');
        await qrCode.toFile(filePath, 'svg');
        console.log(`Generated QR code # ${index + 1}!`);
    } catch (error) {
        // Log any errors during QR code generation
        console.error(`Error generating QR code for ${url}:`, error);
    }
}

// Function to process a CSV file and generate QR codes for each URL
function generateQRFromCSV(csvFilePath) {
    const data = [];

    fs.createReadStream(csvFilePath)
        .pipe(csv())
        .on('data', (row) => {
            // Check for 'qrcode_url', 'qr_code_url', or 'url'
            const url = row.qrcode_url || row.qr_code_url || row.url;
            if (url) {
                data.push(url);
            }
        })
        .on('end', () => {
            if (data.length === 0) {
                console.log('No URLs found in CSV file.');
                return;
            }
            data.forEach((url, index) => createQR(url, index, qrCodeOptions));
            console.log('QR Code generation has commenced! It will be done in a moment');
        })
        .on('error', (oopsie) => {
            // Handle any errors during CSV file reading
            console.error('Oopsie reading CSV file:', oopsie);
        });
}

module.exports = {
    generateQRFromCSV
};