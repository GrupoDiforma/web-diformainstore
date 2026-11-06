 document.addEventListener('DOMContentLoaded', function () {
          var header = document.querySelector('.header-top');
          if (!header) return;

          window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
              header.classList.add('active');
          } else {
              header.classList.remove('active');
          }
      });
      });


const faqsTitles = document.querySelectorAll(".faq .head");

faqsTitles.forEach((faq) => {
  faq.addEventListener("click", () => {
    faq.parentNode.classList.toggle("active");
    const faqContent = faq.nextElementSibling;

    if (faq.parentNode.classList.contains("active")) {
      faqContent.style.height = faqContent.scrollHeight + "px";
    } else {
      faqContent.style.height = "0px";
    }
  });
});




document.addEventListener("DOMContentLoaded", function () {
  const btn = document.getElementById("scrollTopBtn");
  const wrapper = btn.closest(".scroll-top");

  window.addEventListener("scroll", () => {
    if (window.scrollY > 300) {
      wrapper.classList.add("active");
    } else {
      wrapper.classList.remove("active");
    }
  });

  btn.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  });
});

