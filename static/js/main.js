// Main JavaScript for Ramadan Character Styling App
// Updated: 2025-02-16 - Fixed null reference errors

// ============================================
// Security: Protection against Inspect manipulation
// ============================================

// Disable right-click context menu
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    return false;
}, false);

// Disable text selection
document.addEventListener('selectstart', function(e) {
    e.preventDefault();
    return false;
}, false);

// Disable drag and drop
document.addEventListener('dragstart', function(e) {
    e.preventDefault();
    return false;
}, false);

// Disable copy, cut, paste shortcuts
document.addEventListener('keydown', function(e) {
    // Disable F12 (Developer Tools)
    if (e.keyCode === 123) {
        e.preventDefault();
        return false;
    }
    
    // Disable Ctrl+Shift+I (Developer Tools)
    if (e.ctrlKey && e.shiftKey && e.keyCode === 73) {
        e.preventDefault();
        return false;
    }
    
    // Disable Ctrl+Shift+J (Console)
    if (e.ctrlKey && e.shiftKey && e.keyCode === 74) {
        e.preventDefault();
        return false;
    }
    
    // Disable Ctrl+Shift+C (Inspect Element)
    if (e.ctrlKey && e.shiftKey && e.keyCode === 67) {
        e.preventDefault();
        return false;
    }
    
    // Disable Ctrl+U (View Source)
    if (e.ctrlKey && e.keyCode === 85) {
        e.preventDefault();
        return false;
    }
    
    // Disable Ctrl+S (Save Page)
    if (e.ctrlKey && e.keyCode === 83) {
        e.preventDefault();
        return false;
    }
    
    // Disable Ctrl+P (Print)
    if (e.ctrlKey && e.keyCode === 80) {
        e.preventDefault();
        return false;
    }
    
    // Disable Ctrl+Shift+Del (Clear Data)
    if (e.ctrlKey && e.shiftKey && e.keyCode === 46) {
        e.preventDefault();
        return false;
    }
}, false);

// Detect and prevent Developer Tools opening
(function() {
    let devtools = {open: false, orientation: null};
    const threshold = 160;
    
    setInterval(function() {
        if (window.outerHeight - window.innerHeight > threshold || 
            window.outerWidth - window.innerWidth > threshold) {
            if (!devtools.open) {
                devtools.open = true;
                // Redirect or show warning
                document.body.innerHTML = '<div style="text-align:center;padding:50px;font-size:24px;color:#7F5539;">⚠️ تم اكتشاف محاولة فتح أدوات المطور. هذه الصفحة محمية.</div>';
            }
        } else {
            devtools.open = false;
        }
    }, 500);
    
    // Detect console usage
    const originalLog = console.log;
    console.log = function() {
        devtools.open = true;
        originalLog.apply(console, arguments);
    };
})();

// Protect against iframe embedding
if (window.top !== window.self) {
    window.top.location = window.self.location;
}

// Disable image dragging
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    images.forEach(function(img) {
        img.setAttribute('draggable', 'false');
        img.addEventListener('dragstart', function(e) {
            e.preventDefault();
            return false;
        });
    });
});

// ============================================
// End Security Section
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Video Intro Animation Handler - Enhanced
    const videoIntro = document.getElementById('videoIntro');
    const introVideo = document.getElementById('introVideo');
    const skipVideoBtn = document.getElementById('skipVideoBtn');
    const videoLoader = document.getElementById('videoLoader');
    
    // Hide loader when video starts playing
    if (introVideo && videoLoader) {
        introVideo.addEventListener('loadeddata', function() {
            // Video is loaded, hide loader
            setTimeout(function() {
                videoLoader.classList.add('hidden');
            }, 300);
        });
        
        introVideo.addEventListener('canplay', function() {
            // Video can start playing
            videoLoader.classList.add('hidden');
        });
        
        // Show loader if video is still loading
        introVideo.addEventListener('waiting', function() {
            videoLoader.classList.remove('hidden');
        });
    }
    
    // Skip video button
    if (skipVideoBtn) {
        skipVideoBtn.addEventListener('click', function() {
            hideVideoIntro();
        });
        
        // Show skip button after 2 seconds
        setTimeout(function() {
            if (skipVideoBtn && videoIntro && !videoIntro.classList.contains('hidden')) {
                skipVideoBtn.style.opacity = '1';
            }
        }, 2000);
    }
    
    // Hide video when it ends
    if (introVideo) {
        introVideo.addEventListener('ended', function() {
            hideVideoIntro();
        });
        
        // Handle video loading errors
        introVideo.addEventListener('error', function(e) {
            console.warn('Video failed to load, hiding intro:', e);
            if (videoLoader) {
                videoLoader.classList.add('hidden');
            }
            // Hide intro after short delay
            setTimeout(function() {
                hideVideoIntro();
            }, 1000);
        });
        
        // Play video (in case autoplay is blocked)
        introVideo.play().catch(function(error) {
            console.warn('Autoplay blocked:', error);
            // Show skip button immediately if autoplay is blocked
            if (skipVideoBtn) {
                skipVideoBtn.style.opacity = '1';
            }
            // Hide loader if autoplay fails
            if (videoLoader) {
                videoLoader.classList.add('hidden');
            }
        });
        
        // Ensure video is ready
        if (introVideo.readyState >= 2) {
            // Video is already loaded
            if (videoLoader) {
                videoLoader.classList.add('hidden');
            }
        }
    }
    
    function hideVideoIntro() {
        if (videoIntro) {
            // Add fade-out class for smooth animation
            videoIntro.classList.add('fade-out');
            
            // Also add hidden class
            setTimeout(function() {
                videoIntro.classList.add('hidden');
            }, 100);
            
            // Remove from DOM after animation completes
            setTimeout(function() {
                if (videoIntro.parentNode) {
                    videoIntro.remove();
                }
                // Show main content smoothly
                document.body.style.overflow = 'auto';
            }, 1000);
        }
    }
    
    // Prevent body scroll while video is playing
    if (videoIntro && !videoIntro.classList.contains('hidden')) {
        document.body.style.overflow = 'hidden';
    }
    
    // New static characters selector - مع فحص الأمان
    try {
        const categorySelect = document.getElementById('categorySelect');
        const itemSelect = document.getElementById('itemSelect');
        const showCharacterBtn = document.getElementById('showCharacterBtn');
        const generatedImage = document.getElementById('generatedImage');
        const resultPlaceholder = document.getElementById('resultPlaceholder');
        
        // تأكد من وجود العناصر الأساسية
        if (!categorySelect || !itemSelect || !showCharacterBtn || !generatedImage || !resultPlaceholder) {
            console.warn('بعض العناصر المطلوبة غير موجودة في الصفحة');
            return; // توقف عن تنفيذ الكود لو العناصر مش موجودة
        }

    // Static data for characters (يمكنك تغيير المسارات والأسماء براحتك)
    const charactersData = {
        // Category 1: Arab Characters (Nationalities)
        arabCharacters: [
            { id: 'egyptian',   name: 'Egyptian / مصري',                     imageUrl: '/static/images/generated/arab-egyptian.jpg' },
            { id: 'saudi',      name: 'Saudi / سعودي',                       imageUrl: '/static/images/generated/arab-saudi.jpg' },
            { id: 'moroccan',   name: 'Moroccan / مغربي',                    imageUrl: '/static/images/generated/arab-moroccan.jpg' },
            { id: 'emirati',    name: 'Emirati / إماراتي',                   imageUrl: '/static/images/generated/arab-emirati.jpg' }
        ],

        // Category 2: Foreign Characters (Nationalities)
        foreignCharacters: [
            { id: 'italian',    name: 'Italian / إيطالي',                    imageUrl: '/static/images/generated/foreign-italian.jpg' },
            { id: 'american_cowboy', name: 'American (Cowboy) / أمريكي (راعي بقر)', imageUrl: '/static/images/generated/foreign-american-cowboy.jpg' },
            { id: 'japanese',   name: 'Japanese / ياباني',                   imageUrl: '/static/images/generated/foreign-japanese.jpg' },
            { id: 'mexican',    name: 'Mexican / مكسيكي',                    imageUrl: '/static/images/generated/foreign-mexican.jpg' },
            { id: 'french',     name: 'French / فرنسي',                      imageUrl: '/static/images/generated/foreign-french.jpg' },
            { id: 'indian',     name: 'Indian / هندي',                       imageUrl: '/static/images/generated/foreign-indian.jpg' },
            { id: 'british',    name: 'British / بريطاني',                   imageUrl: '/static/images/generated/foreign-british.jpg' },
            { id: 'spanish',    name: 'Spanish / إسباني',                    imageUrl: '/static/images/generated/foreign-spanish.jpg' },
            { id: 'russian',    name: 'Russian / روسي',                      imageUrl: '/static/images/generated/foreign-russian.jpg' },
            { id: 'brazilian',  name: 'Brazilian / برازيلي',                imageUrl: '/static/images/generated/foreign-brazilian.jpg' }
        ],

        // Category 3: Jobs & Professions
        jobs: [
            { id: 'doctor',         name: 'Doctor / طبيب',                   imageUrl: '/static/images/generated/job-doctor.jpg' },
            { id: 'chef',           name: 'Chef / طباخ (شيف)',               imageUrl: '/static/images/generated/job-chef.jpg' },
            { id: 'astronaut',      name: 'Astronaut / رائد فضاء',           imageUrl: '/static/images/generated/job-astronaut.jpg' },
            { id: 'firefighter',    name: 'Firefighter / رجل إطفاء',         imageUrl: '/static/images/generated/job-firefighter.jpg' },
            { id: 'construction_engineer', name: 'Construction Engineer / مهندس بناء', imageUrl: '/static/images/generated/job-construction-engineer.jpg' },
            { id: 'pilot',          name: 'Pilot / طيار',                    imageUrl: '/static/images/generated/job-pilot.jpg' },
            { id: 'farmer',         name: 'Farmer / فلاح (مزارع)',          imageUrl: '/static/images/generated/job-farmer.jpg' },
            { id: 'judge',          name: 'Judge / قاضي',                    imageUrl: '/static/images/generated/job-judge.jpg' },
            { id: 'delivery_rider', name: 'Delivery Rider / عامل توصيل (دليفري)', imageUrl: '/static/images/generated/job-delivery-rider.jpg' }
        ],

        // Category 4: Football Clubs
        clubs: [
            { id: 'alahly',        name: 'Al Ahly SC / النادي الأهلي المصري',        imageUrl: '/static/images/generated/club-alahly.jpg' },
            { id: 'zamalek',       name: 'Zamalek SC / نادي الزمالك',               imageUrl: '/static/images/generated/club-zamalek.jpg' },
            { id: 'alhilal',       name: 'Al Hilal SFC / نادي الهلال السعودي',      imageUrl: '/static/images/generated/club-alhilal.jpg' },
            { id: 'real_madrid',   name: 'Real Madrid / ريال مدريد',                imageUrl: '/static/images/generated/club-real-madrid.jpg' },
            { id: 'barcelona',     name: 'FC Barcelona / برشلونة',                  imageUrl: '/static/images/generated/club-barcelona.jpg' },
            { id: 'man_utd',       name: 'Manchester United / مانشستر يونايتد',     imageUrl: '/static/images/generated/club-man-utd.jpg' },
            { id: 'liverpool',     name: 'Liverpool FC / ليفربول',                  imageUrl: '/static/images/generated/club-liverpool.jpg' },
            { id: 'bayern',        name: 'Bayern Munich / بايرن ميونخ',             imageUrl: '/static/images/generated/club-bayern.jpg' },
            { id: 'juventus',      name: 'Juventus FC / يوفنتوس',                   imageUrl: '/static/images/generated/club-juventus.jpg' },
            { id: 'psg',           name: 'Paris Saint-Germain (PSG) / باريس سان جيرمان', imageUrl: '/static/images/generated/club-psg.jpg' }
        ]
    };

    // Function to check if image exists
    async function checkImageExists(imageUrl) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = function() {
                resolve(true);
            };
            img.onerror = function() {
                resolve(false);
            };
            // Set timeout to avoid hanging
            setTimeout(() => resolve(false), 3000);
            img.src = imageUrl;
        });
    }

    function clearResult() {
        if (generatedImage) {
            generatedImage.style.display = 'none';
            generatedImage.src = '';
        }
        if (resultPlaceholder) {
            resultPlaceholder.style.display = 'flex';
        }
    }

    function populateItems(categoryKey) {
        if (!itemSelect) return;
        itemSelect.innerHTML = '';

        if (!categoryKey || !charactersData[categoryKey]) {
            itemSelect.disabled = true;
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = 'اختر أولاً الفئة من الأعلى';
            itemSelect.appendChild(opt);
            clearResult();
            return;
        }

        const defaultOpt = document.createElement('option');
        defaultOpt.value = '';
        defaultOpt.textContent = 'اختر التصميم...';
        itemSelect.appendChild(defaultOpt);

        charactersData[categoryKey].forEach(item => {
            const opt = document.createElement('option');
            opt.value = item.id;
            opt.textContent = item.name;
            itemSelect.appendChild(opt);
        });

        itemSelect.disabled = false;
        clearResult();
    }

    // نجعل الدالة متاحة عالميًا عشان نقدر نستدعيها من الـ HTML مباشرة
    window.handleCategoryChange = function (categoryKey) {
        populateItems(categoryKey);
    };

    if (showCharacterBtn) {
        showCharacterBtn.addEventListener('click', async function () {
            const categoryKey = categorySelect ? categorySelect.value : '';
            const itemId = itemSelect ? itemSelect.value : '';

            if (!categoryKey) {
                alert('من فضلك اختر الفئة أولاً');
                return;
            }
            if (!itemId) {
                alert('من فضلك اختر التصميم المطلوب');
                return;
            }

            const items = charactersData[categoryKey] || [];
            const selectedItem = items.find(i => i.id === itemId);
            if (!selectedItem) {
                alert('حدث خطأ في اختيار التصميم، حاول مرة أخرى');
                return;
            }

            if (resultPlaceholder) {
                resultPlaceholder.style.display = 'none';
                resultPlaceholder.innerHTML = '<p>جارٍ التحميل...</p>';
            }

            if (generatedImage) {
                // Reset any previous error state
                generatedImage.onerror = null;
                generatedImage.onload = null;
                
                // Check if image exists before loading
                const imageExists = await checkImageExists(selectedItem.imageUrl);
                
                if (!imageExists) {
                    // Image doesn't exist, show placeholder message
                    generatedImage.style.display = 'none';
                    if (resultPlaceholder) {
                        resultPlaceholder.style.display = 'flex';
                        resultPlaceholder.innerHTML = '<p>الصورة غير متوفرة حالياً. يرجى اختيار تصميم آخر.</p>';
                    }
                    return;
                }
                
                // Set up error handler before loading (as backup)
                generatedImage.onerror = function() {
                    generatedImage.style.display = 'none';
                    if (resultPlaceholder) {
                        resultPlaceholder.style.display = 'flex';
                        resultPlaceholder.innerHTML = '<p>الصورة غير متوفرة حالياً. يرجى اختيار تصميم آخر.</p>';
                    }
                    return false;
                };
                
                // Image exists, load it
                generatedImage.onload = function() {
                    if (resultPlaceholder) {
                        resultPlaceholder.style.display = 'none';
                    }
                    // Show download button when image loads
                    const downloadBtn = document.getElementById('downloadGeneratedBtn');
                    if (downloadBtn) {
                        downloadBtn.style.display = 'flex';
                    }
                };
                
                generatedImage.src = selectedItem.imageUrl;
                generatedImage.style.display = 'block';
                generatedImage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        });
    }

        // Global error handler as backup (in case onerror doesn't work)
        if (generatedImage) {
            generatedImage.addEventListener('error', function (e) {
                // Prevent any default error behavior
                e.preventDefault();
                e.stopPropagation();
                
                // Handle image loading errors gracefully without showing alert
                generatedImage.style.display = 'none';
                if (resultPlaceholder) {
                    resultPlaceholder.style.display = 'flex';
                    resultPlaceholder.innerHTML = '<p>الصورة غير متوفرة حالياً. يرجى اختيار تصميم آخر.</p>';
                }
                return false;
            }, true); // Use capture phase to catch errors early
        }
    } catch (error) {
        console.error('حدث خطأ في تحميل الكود:', error);
    }
});
