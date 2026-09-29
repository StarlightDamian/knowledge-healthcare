/** Plain-text paragraphs and bullet lists only. Content is never interpreted as HTML. */
export function textBlocks(value) {
  const blocks=[];
  let paragraph=[];
  const flush=()=>{if(paragraph.length){blocks.push({type:'paragraph',text:paragraph.join(' ')});paragraph=[];}};
  for(const line of String(value??'').replace(/\r\n?/g,'\n').split('\n')) {
    const text=line.trim();
    if(!text){flush();continue;}
    if(text.startsWith('- ')) {
      flush();
      if(blocks.at(-1)?.type!=='list')blocks.push({type:'list',items:[]});
      blocks.at(-1).items.push(text.slice(2));
    } else paragraph.push(text);
  }
  flush();return blocks;
}

export function firstParagraph(value) {
  const first=textBlocks(value)[0];
  return first?.type==='list'?first.items[0]:first?.text??'';
}

export function appendText(container,value) {
  for(const block of textBlocks(value)) {
    const element=document.createElement(block.type==='list'?'ul':'p');
    if(block.type==='list') {
      for(const item of block.items){const li=document.createElement('li');li.textContent=item;element.append(li);}
    } else element.textContent=block.text;
    container.append(element);
  }
}
