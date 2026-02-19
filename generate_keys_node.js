// 生成用于 botcoin.farm 的 Ed25519 密钥对
// 使用 Node.js 内置的 crypto 库

const crypto = require('crypto');

// 生成 Ed25519 密钥对
function generateEd25519Keypair() {
    try {
        const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519', {
            publicKeyEncoding: { type: 'spki', format: 'der' },
            privateKeyEncoding: { type: 'pkcs8', format: 'der' }
        });
        
        // 提取原始密钥字节
        // 对于 DER 编码的密钥，我们需要提取原始的 32 字节部分
        const rawPublicKey = publicKey.subarray(-32); // 最后32字节是公钥
        const rawPrivateKey = privateKey.subarray(-32); // 最后32字节是私钥
        
        // 转换为 base64
        const publicKeyB64 = rawPublicKey.toString('base64');
        const privateKeyB64 = rawPrivateKey.toString('base64');
        
        return { publicKey: publicKeyB64, privateKey: privateKeyB64 };
    } catch (error) {
        console.error('生成 Ed25519 密钥对失败:', error.message);
        return null;
    }
}

// 更准确的密钥提取方法
function generateEd25519KeypairCorrect() {
    try {
        const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519', {
            publicKeyEncoding: { type: 'spki', format: 'pem' },
            privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
        });
        
        // 从 PEM 格式中提取原始密钥
        // Ed25519 公钥在 SPKI 中的固定位置
        const publicKeyBuffer = Buffer.from(publicKey.split('\n').slice(1, -1).join(''), 'base64');
        // SPKI 结构中，公钥在末尾的 32 字节
        const rawPublicKey = publicKeyBuffer.subarray(-32);
        
        // 从 PEM 格式中提取原始私钥
        const privateKeyBuffer = Buffer.from(privateKey.split('\n').slice(1, -1).join(''), 'base64');
        // PKCS8 结构比较复杂，需要解析 ASN.1 结构
        // 对于 Ed25519，私钥通常是末尾的 32 字节
        const rawPrivateKey = privateKeyBuffer.subarray(-64, -32); // Ed25519 私钥通常是 32 字节，在 PKCS8 中位于特定位置
        
        // 更准确的方法：使用 JWK 格式
        const { publicKey: pubJWK, privateKey: privJWK } = crypto.generateKeyPairSync('ed25519', {
            publicKeyEncoding: { type: 'spki', format: 'jwk' },
            privateKeyEncoding: { type: 'pkcs8', format: 'jwk' }
        });
        
        // JWK 格式中的 x 是公钥，d 是私钥，都是 base64url 编码
        const jwkPublicKey = Buffer.from(pubJWK.x, 'base64'); // base64url 解码后转为 base64
        const jwkPrivateKey = Buffer.from(privJWK.d, 'base64'); // base64url 解码后转为 base64
        
        return {
            publicKey: jwkPublicKey.toString('base64'),
            privateKey: jwkPrivateKey.toString('base64')
        };
    } catch (error) {
        console.error('生成 Ed25519 密钥对失败:', error.message);
        return null;
    }
}

// 最可靠的方法
function generateKeypairWithJWK() {
    try {
        const { publicKey, privateKey } = crypto.generateKeyPairSync('ed25519', {
            publicKeyEncoding: { type: 'spki', format: 'jwk' },
            privateKeyEncoding: { type: 'pkcs8', format: 'jwk' }
        });
        
        // 转换 base64url 到标准 base64
        function base64urlToBase64(base64url) {
            // 将 base64url 转换为标准 base64
            let base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
            // 添加填充
            const padding = '='.repeat((4 - base64.length % 4) % 4);
            return base64 + padding;
        }
        
        const publicKeyB64 = base64urlToBase64(publicKey.x);
        const privateKeyB64 = base64urlToBase64(privateKey.d);
        
        return {
            publicKey: publicKeyB64,
            privateKey: privateKeyB64
        };
    } catch (error) {
        console.error('生成 Ed25519 密钥对失败:', error.message);
        return null;
    }
}

// 主函数
function main() {
    console.log("正在生成 Ed25519 密钥对用于 botcoin.farm...");
    
    const keys = generateKeypairWithJWK();
    
    if (keys) {
        console.log("\n=== Botcoin.farm 密钥对 ===");
        console.log(`公钥 (publicKey): ${keys.publicKey}`);
        console.log(`私钥 (secretKey): ${keys.privateKey}`);
        console.log("========================="); 
        console.log("重要提示：");
        console.log("1. 请安全保存您的私钥，切勿泄露给他人");
        console.log("2. 私钥一旦丢失无法找回");
        console.log("3. 公钥可以安全地分享用于注册");
        console.log("=========================");
        
        // 验证密钥长度
        console.log(`\n密钥验证:`);
        console.log(`公钥长度: ${keys.publicKey.length} 字符 (应为43或44)`);
        console.log(`私钥长度: ${keys.privateKey.length} 字符 (应为43或44)`);
        
        console.log("\n要使用这些密钥，请:");
        console.log("1. 保存好私钥，存放在安全的位置");
        console.log("2. 使用公钥进行 botcoin.farm 注册");
        console.log("3. 在需要签名交易时，使用私钥进行签名");
    } else {
        console.log("密钥生成失败，请检查环境是否支持 Ed25519 生成");
    }
}

// 运行主函数
main();