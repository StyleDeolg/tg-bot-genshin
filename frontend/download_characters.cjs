const https = require('https');
const fs = require('fs');
const path = require('path');

const characters = [
    { name: 'Lumine', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Lumine.png' },
    { name: 'Aether', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Aether.png' },
    { name: 'Paimon', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Paimon.png' },
    { name: 'Venti', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Venti.png' },
    { name: 'Zhongli', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Zhongli.png' },
    { name: 'Keqing', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Keqing.png' },
    { name: 'Diluc', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Diluc.png' },
    { name: 'Jean', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Jean.png' },
    { name: 'Tartaglia', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Tartaglia.png' },
    { name: 'Hutao', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Hutao.png' },
    { name: 'Ganyu', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Ganyu.png' },
    { name: 'Xiao', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Xiao.png' },
    { name: 'Kokomi', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Kokomi.png' },
    { name: 'Shougun', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Shougun.png' },
    { name: 'KamisatoAyaka', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_KamisatoAyaka.png' },
    { name: 'Albedo', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Albedo.png' },
    { name: 'Kazuha', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Kazuha.png' },
    { name: 'Nahida', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Nahida.png' },
    { name: 'Sucrose', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Sucrose.png' },
    { name: 'Fischl', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Fischl.png' },
    { name: 'Mona', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Mona.png' },
    { name: 'Bennett', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Bennett.png' },
    { name: 'Rosaria', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Rosaria.png' },
    { name: 'Noel', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Noel.png' },
    { name: 'Razor', url: 'https://upload-os-bbs.mihoyo.com/game_record/genshin/character_icon/UI_AvatarIcon_Razor.png' },
];

const downloadDir = path.join(__dirname, 'public', 'characters');

if (!fs.existsSync(downloadDir)) {
    fs.mkdirSync(downloadDir, { recursive: true });
}

characters.forEach((char) => {
    const filePath = path.join(downloadDir, `${char.name}.png`);
    const file = fs.createWriteStream(filePath);

    https.get(char.url, (response) => {
        response.pipe(file);
        file.on('finish', () => {
            file.close();
            console.log(`✅ Скачан: ${char.name}`);
        });
    }).on('error', (err) => {
        fs.unlink(filePath, () => { });
        console.error(`❌ Ошибка скачивания ${char.name}:`, err.message);
    });
});

console.log('📥 Начинаю скачивание картинок...');