// A complete film: open a page, scroll to a section, point at it, wait for something slow,
// and cut the wait short. Run: node film.mjs run example-film.mjs
export const options = {
  name: "example",
  width: 1440,
  height: 900,
  dark: false,              // null = the page decides; true / false = force the colour scheme
  url: "https://externalsoul.com/u/robocop",
  webp: 800,                // also write an animated WebP 800 px wide (for the Site app)
};

export default async function film(f) {
  await f.rec.start();
  await f.hold(1200);                                   // let the first frame breathe
  await f.moveTo({ x: 900, y: 520 }, { ms: 900 });
  await f.hold(600);
  f.mark("scroll");
  await f.page.evaluate(() => window.scrollBy({ top: 700, behavior: "smooth" }));
  await f.hold(2500);
  f.mark("end");
  return {
    cut: [{ to: "scroll" }, { from: "scroll", to: "end", speed: 1.5 }],
    posterAt: "scroll",
  };
}
