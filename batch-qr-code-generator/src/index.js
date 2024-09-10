const { QRCodeCanvas } = require('@loskir/styled-qr-code-node');
const csv = require('csv-parser');
const fs = require('fs-extra');
const path = require('path');

// Import the QR code options from options.json
const qrCodeOptions = require('./options.json');

// Function to generate QR code
async function createQR(url, filename, options) {
    options.data = url;
    const qrCode = new QRCodeCanvas({ ...options, data: url });

    try {
        // Ensure the qr_codes directory exists
        await fs.ensureDir('./qr_codes');

        // Remove the .pdf extension and add _qr.svg
        const svgFilename = filename.replace(/\.pdf$/, '_qr.svg');
        const filePath = path.join('./qr_codes', svgFilename);

        // Uncomment this if you want to do PNG instead: 
        // await qrCode.toFile(`./qr_codes/qr_${index + 1}.png`, 'png');

        await qrCode.toFile(filePath, 'svg');
        console.log(`Generated QR code: ${svgFilename}`);
        return true;
    } catch (error) {
        // Log any errors during QR code generation
        console.error(`Error generating QR code for ${url}:`, error);
        return false;
    }
}

// Function to process a CSV file and generate QR codes for each URL
async function generateQRFromCSV(csvFilePath) {
    const data = [];
    let totalGenerated = 0;

    return new Promise((resolve, reject) => {
        fs.createReadStream(csvFilePath)
            .pipe(csv())
            .on('data', (row) => {
                const url = row.qrcode_url || row.qr_code_url || row.url;
                const filename = row.card_filename;
                if (url && filename) {
                    data.push({ url, filename });
                }
            })
            .on('end', async () => {
                if (data.length === 0) {
                    console.log('No valid data found in CSV file.');
                    resolve(0);
                    return;
                }

                console.log('QR Code generation has commenced! Please wait...');

                for (const { url, filename } of data) {
                    const success = await createQR(url, filename, qrCodeOptions);
                    if (success) totalGenerated++;
                }

                resolve(totalGenerated);
            })
            .on('error', (error) => {
                console.error('Error reading CSV file:', error);
                reject(error);
            });
    });
}

module.exports = {
    generateQRFromCSV
};