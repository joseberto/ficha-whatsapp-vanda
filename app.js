(() => {
  "use strict";

  const CENTRAL_PHONE = "5585920013309";
  const DEFAULT_REFERRER = "Vanda Silva";
  const params = new URLSearchParams(window.location.search);
  const referrer = cleanName(params.get("indicado_por")) || DEFAULT_REFERRER;

  const form = document.getElementById("registration-form");
  const formCard = document.getElementById("form-card");
  const resultCard = document.getElementById("result-card");
  const errorBox = document.getElementById("form-error");
  document.getElementById("referrer-name").textContent = referrer;

  let registration = null;

  function cleanName(value) {
    return String(value || "").replace(/[<>\r\n]/g, " ").replace(/\s+/g, " ").trim().slice(0, 100);
  }

  function onlyDigits(value) {
    return String(value || "").replace(/\D/g, "");
  }

  function formatCPF(value) {
    const digits = onlyDigits(value).slice(0, 11);
    return digits.replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d)/, "$1.$2").replace(/(\d{3})(\d{1,2})$/, "$1-$2");
  }

  function formatPhone(value) {
    const digits = onlyDigits(value).slice(0, 11);
    if (digits.length <= 10) return digits.replace(/(\d{2})(\d)/, "($1) $2").replace(/(\d{4})(\d)/, "$1-$2");
    return digits.replace(/(\d{2})(\d)/, "($1) $2").replace(/(\d{5})(\d)/, "$1-$2");
  }

  function validCPF(value) {
    const cpf = onlyDigits(value);
    if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
    let sum = 0;
    for (let i = 0; i < 9; i++) sum += Number(cpf[i]) * (10 - i);
    let digit = (sum * 10) % 11;
    if (digit === 10) digit = 0;
    if (digit !== Number(cpf[9])) return false;
    sum = 0;
    for (let i = 0; i < 10; i++) sum += Number(cpf[i]) * (11 - i);
    digit = (sum * 10) % 11;
    if (digit === 10) digit = 0;
    return digit === Number(cpf[10]);
  }

  function dateBR(value) {
    if (!value) return "";
    const [year, month, day] = value.split("-");
    return `${day}/${month}/${year}`;
  }

  function currentBaseUrl() {
    return `${window.location.origin}${window.location.pathname}`;
  }

  function referralLink(name) {
    return `${currentBaseUrl()}?indicado_por=${encodeURIComponent(name)}`;
  }

  function messageText(data) {
    return [
      "*FICHA DE CADASTRO*",
      "",
      `*Nome:* ${data.nome}`,
      `*Nº do título:* ${data.titulo}`,
      `*Zona:* ${data.zona}`,
      `*Seção:* ${data.secao}`,
      `*Endereço:* ${data.endereco}`,
      `*Nascimento:* ${dateBR(data.nascimento)}`,
      `*CPF:* ${formatCPF(data.cpf)}`,
      `*Celular:* ${formatPhone(data.celular)}`,
      `*Indicado por:* ${referrer}`,
      "",
      "Autorização para cadastro, contato e relatório interno: SIM",
    ].join("\n");
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.hidden = false;
    errorBox.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function collect() {
    const data = Object.fromEntries(new FormData(form).entries());
    data.nome = cleanName(data.nome);
    data.titulo = onlyDigits(data.titulo);
    data.zona = onlyDigits(data.zona);
    data.secao = onlyDigits(data.secao);
    data.cpf = onlyDigits(data.cpf);
    data.celular = onlyDigits(data.celular);
    data.endereco = String(data.endereco || "").replace(/[<>\r\n]/g, " ").replace(/\s+/g, " ").trim();
    return data;
  }

  function validate(data) {
    if (!data.nome || !data.titulo || !data.zona || !data.secao || !data.endereco || !data.nascimento || !data.cpf || !data.celular) return "Preencha todos os campos da ficha.";
    if (data.nome.split(" ").length < 2) return "Digite o nome completo.";
    if (!validCPF(data.cpf)) return "Confira o CPF. Ele parece estar incorreto.";
    if (data.celular.length < 10 || data.celular.length > 11) return "Digite um celular válido com DDD.";
    if (!document.getElementById("consentimento").checked) return "Marque a autorização para continuar.";
    return "";
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    errorBox.hidden = true;
    const data = collect();
    const error = validate(data);
    if (error) return showError(error);
    registration = data;
    formCard.hidden = true;
    resultCard.hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  document.getElementById("cpf").addEventListener("input", (event) => { event.target.value = formatCPF(event.target.value); });
  document.getElementById("celular").addEventListener("input", (event) => { event.target.value = formatPhone(event.target.value); });

  document.getElementById("send-whatsapp").addEventListener("click", () => {
    if (!registration) return;
    const url = `https://wa.me/${CENTRAL_PHONE}?text=${encodeURIComponent(messageText(registration))}`;
    window.location.href = url;
  });

  document.getElementById("share-referral").addEventListener("click", async () => {
    if (!registration) return;
    const link = referralLink(registration.nome);
    const text = `Olá! Preencha esta ficha de cadastro. Você será registrado como indicado por ${registration.nome}.`;
    if (navigator.share) {
      try { await navigator.share({ title: "Ficha de Cadastro", text, url: link }); return; } catch (error) { if (error.name === "AbortError") return; }
    }
    await navigator.clipboard.writeText(`${text}\n${link}`);
    alert("Link copiado. Agora cole e envie no WhatsApp.");
  });

  function wrapText(ctx, text, x, y, maxWidth, lineHeight, maxLines = 3) {
    const words = String(text).split(" ");
    let line = "", lines = 0;
    for (const word of words) {
      const test = `${line}${word} `;
      if (ctx.measureText(test).width > maxWidth && line) {
        ctx.fillText(line.trim(), x, y + lines * lineHeight);
        line = `${word} `;
        if (++lines >= maxLines) return y + lines * lineHeight;
      } else line = test;
    }
    ctx.fillText(line.trim(), x, y + lines * lineHeight);
    return y + (lines + 1) * lineHeight;
  }

  function drawImage(data) {
    const canvas = document.getElementById("card-canvas");
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#123b68";
    ctx.fillRect(0, 0, canvas.width, 180);
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 56px Arial";
    ctx.textAlign = "center";
    ctx.fillText("FICHA DE CADASTRO", 540, 110);
    ctx.textAlign = "left";

    const fields = [
      ["INDICADO POR", referrer], ["NOME COMPLETO", data.nome],
      ["Nº DO TÍTULO", data.titulo], ["ZONA / SEÇÃO", `${data.zona} / ${data.secao}`],
      ["ENDEREÇO COMPLETO", data.endereco], ["DATA DE NASCIMENTO", dateBR(data.nascimento)],
      ["CPF", formatCPF(data.cpf)], ["CELULAR", formatPhone(data.celular)],
    ];
    let y = 235;
    for (const [label, value] of fields) {
      ctx.fillStyle = "#123b68";
      ctx.font = "bold 24px Arial";
      ctx.fillText(label, 70, y);
      ctx.fillStyle = "#202a34";
      ctx.font = "32px Arial";
      y = wrapText(ctx, value, 70, y + 43, 940, 42, label === "ENDEREÇO COMPLETO" ? 3 : 2) + 36;
      ctx.strokeStyle = "#c6d2de";
      ctx.beginPath(); ctx.moveTo(70, y - 14); ctx.lineTo(1010, y - 14); ctx.stroke();
    }
    ctx.fillStyle = "#66717d";
    ctx.font = "20px Arial";
    wrapText(ctx, "Cadastro enviado pelo WhatsApp com autorização para uso em cadastro, contato e relatório interno.", 70, 1280, 940, 28, 2);
    return canvas;
  }

  document.getElementById("download-image").addEventListener("click", () => {
    if (!registration) return;
    const canvas = drawImage(registration);
    const link = document.createElement("a");
    link.download = `ficha-${registration.nome.toLowerCase().replace(/[^a-z0-9]+/g, "-")}.png`;
    link.href = canvas.toDataURL("image/png");
    link.click();
  });

  document.getElementById("edit-form").addEventListener("click", () => {
    resultCard.hidden = true;
    formCard.hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
})();
