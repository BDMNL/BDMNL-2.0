const header = document.querySelector("[data-header]");
const navToggle = document.querySelector("[data-nav-toggle]");
const navMenu = document.querySelector("[data-nav-menu]");
const navBackdrop = document.querySelector("[data-nav-backdrop]");
const revealItems = document.querySelectorAll(".reveal");
const faqItems = document.querySelectorAll(".faq-item");
const statItems = document.querySelectorAll("[data-count-to]");
const tiltCards = document.querySelectorAll("[data-tilt-card]");

const updateHeader = () => {
  header?.classList.toggle("is-scrolled", window.scrollY > 12);
};

updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

const closeNavigation = () => {
  navToggle?.setAttribute("aria-expanded", "false");
  navMenu?.classList.remove("is-open");
  navBackdrop?.classList.remove("is-open");
  document.body.classList.remove("nav-open");
};

navToggle?.addEventListener("click", () => {
  const isOpen = navToggle.getAttribute("aria-expanded") === "true";

  navToggle.setAttribute("aria-expanded", String(!isOpen));
  navMenu?.classList.toggle("is-open", !isOpen);
  navBackdrop?.classList.toggle("is-open", !isOpen);
  document.body.classList.toggle("nav-open", !isOpen);
});

navBackdrop?.addEventListener("click", closeNavigation);

navMenu?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", closeNavigation);
});

const formatStatValue = (value, decimals) => {
  if (decimals > 0) {
    return value.toFixed(decimals);
  }

  return Math.round(value).toString();
};

const animateStat = (item) => {
  if (item.dataset.counted === "true") {
    return;
  }

  const target = Number(item.dataset.countTo || 0);
  const decimals = Number(item.dataset.countDecimals || 0);
  const prefix = item.dataset.countPrefix || "";
  const suffix = item.dataset.countSuffix || "";
  const duration = 1100;
  const start = performance.now();

  item.dataset.counted = "true";

  const tick = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    item.textContent = `${prefix}${formatStatValue(target * eased, decimals)}${suffix}`;

    if (progress < 1) {
      requestAnimationFrame(tick);
    }
  };

  requestAnimationFrame(tick);
};

if ("IntersectionObserver" in window) {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    {
      threshold: 0.14,
      rootMargin: "0px 0px -80px",
    },
  );

  revealItems.forEach((item) => revealObserver.observe(item));

  const statObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        animateStat(entry.target);
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.55 },
  );

  statItems.forEach((item) => statObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add("is-visible"));
  statItems.forEach(animateStat);
}

faqItems.forEach((item) => {
  const button = item.querySelector("button");
  const answer = item.querySelector(".faq-answer");

  button?.addEventListener("click", () => {
    const isOpen = item.classList.contains("is-open");

    faqItems.forEach((otherItem) => {
      const otherButton = otherItem.querySelector("button");
      const otherAnswer = otherItem.querySelector(".faq-answer");

      otherItem.classList.remove("is-open");
      otherButton?.setAttribute("aria-expanded", "false");

      if (otherAnswer) {
        otherAnswer.style.maxHeight = null;
      }
    });

    if (isOpen || !answer) {
      return;
    }

    item.classList.add("is-open");
    button.setAttribute("aria-expanded", "true");
    answer.style.maxHeight = `${answer.scrollHeight}px`;
  });
});

tiltCards.forEach((card) => {
  card.addEventListener("pointermove", (event) => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    const rect = card.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;

    card.style.transform = `rotateX(${y * -4}deg) rotateY(${x * 6}deg) translateY(-6px)`;
  });

  card.addEventListener("pointerleave", () => {
    card.style.transform = "";
  });
});
