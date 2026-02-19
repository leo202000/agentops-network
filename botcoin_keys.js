// 生成 Ed25519 密钥对用于 botcoin.farm
// 需要安装 tweetnacl 和 tweetnacl-util 库
// npm install tweetnacl tweetnacl-util

import nacl from 'tweetnacl';
import { encodeBase64 } from 'tweetnacl-util';

// 生成密钥对
const keyPair = nacl.sign.keyPair();
const publicKey = encodeBase64(keyPair.publicKey); // 44 字符
const secretKey = encodeBase64(keyPair.secretKey); // 88 字符

console.log("=== Botcoin.farm 密钥对 ===");
console.log("公钥 (publicKey):", publicKey);
console.log("私钥 (secretKey):", secretKey);
console.log("=========================");
console.log("重要提示：");
console.log("1. 请安全保存您的私钥，切勿泄露给他人");
console.log("2. 私钥一旦丢失无法找回");
console.log("3. 公钥可以安全地分享用于注册");
console.log("=========================");

// 密钥验证函数
function verifyKeys() {
    console.log("\n密钥生成验证:");
    console.log("公钥长度:", publicKey.length, "字符 (应为44)");
    console.log("私钥长度:", secretKey.length, "字符 (应为88)");
    
    if (publicKey.length === 44 && secretKey.length === 88) {
        console.log("✓ 密钥对生成成功");
    } else {
        console.log("✗ 密钥对生成失败");
    }
}

verifyKeys();

// 签名交易示例函数
function signTransactionExample(transaction, secretKey) {
    import { decodeBase64 } from 'tweetnacl-util';
    
    const message = JSON.stringify(transaction);
    const messageBytes = new TextEncoder().encode(message);
    const secretKeyBytes = decodeBase64(secretKey);
    const signature = nacl.sign.detached(messageBytes, secretKeyBytes);
    return encodeBase64(signature);
}

// 使用示例（注意：这只是示例，请不要在实际中使用）
/*
const exampleTransaction = {
    type: 'solve',
    huntId: 1,
    answer: 'justice',
    publicKey: publicKey,
    timestamp: Date.now()
};

const signature = signTransactionExample(exampleTransaction, secretKey);
console.log("示例签名:", signature);
*/