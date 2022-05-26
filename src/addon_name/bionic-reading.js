/**
 *
 * We try to respect that people use various note types
 * which may do 'weird' stuff.
 * Elements may have event listeners that can be removed if we just innerHTML stuff
 * <i> may be styled 'i { display: block }', etc.
 *
 * Another problem that complicate the design of this script is that
 * a word may not be cleanly separated by html tags.
 * e.g. "A<i>long</i>word"
 *
 */

(function () {
  /**
   * @param {String} text
   * @returns {number}
   */
  function getBoldLength(text) {
    return Math.floor(text.length / 2);
  }

  /**
   * Run funct on each same-line-breaking nodes.
   * You should run funct on remaining nodes after running this function
   *
   * @param {Node} elem
   * @param {Node[]} - list of text nodes.
   * @param {(nodes: Node[]) -> void} funct - nodes: non empty list of text nodes
   *    node may be a text node, or an element.
   * @returns {void}
   */
  function forEachChildTextNodes(elem, nodes, funct) {
    const children = elem.childNodes;
    for (const child of children) {
      if (child.nodeType === Node.ELEMENT_NODE) {
        const style = window.getComputedStyle(child);
        if (style === "inline" || style === "inline-block") {
          forEachChildTextNodes(child, nodes, funct);
        } else {
          if (nodes.length > 0) {
            funct(nodes);
            nodes = [];
          }
          forEachChildTextNodes(child, nodes, funct);
        }
      } else if (child.nodeType === Node.TEXT_NODE) {
        nodes.push(child);
      }
    }
    if (nodes.length > 0) funct(nodes);
  }

  /**
   * Replace node with nodes
   * @param {Node} node
   * @param {Node[]} nodes
   */
  function replaceNode(node, nodes) {
    const parent = node.parentNode;
    for (let add of nodes) {
      parent.insertBefore(add, node);
    }
    parent.removeChild(node);
  }

  function newBoldElement(text) {
    const elem = document.createElement("b");
    elem.innerText = text;
    return elem;
  }

  /**
   * Bionic-bold each word in nodes text
   * @param {Node[]} nodes - list of text nodes
   */
  function boldNodes(nodes) {
    // Identify a word (start..end) -> get bold length
    // -> add nodes for the word -> when one node done, replace original node
    // At finish, startNodeIndex == endNodeIndex == nodes.length, startPos == endPos == 0
    console.log(nodes);
    let startNodeIndex = 0;
    let startPos = 0;
    let endNodeIndex = 0;
    let endPos = 0; // Can be considered position of the whitespace
    let textContents = nodes.map((node) => node.textContent);
    let replaceNodes = [];

    while (!(startNodeIndex === nodes.length && startPos === 0)) {
      // identify a word
      let word = "";

      while (endNodeIndex < nodes.length) {
        const nextPos = textContents[endNodeIndex].indexOf(" ", endPos);
        if (nextPos !== -1) {
          word += textContents[endNodeIndex].substring(endPos, nextPos);
          endPos = nextPos;
          break;
        } else {
          word += textContents[endNodeIndex].substring(endPos);
          endPos = 0;
          endNodeIndex += 1;
        }
      }
      // word may be ""
      let remainingBoldLength = getBoldLength(word);

      while (remainingBoldLength > 0) {
        const textContent = textContents[startNodeIndex];

        if (textContent.length <= startPos + remainingBoldLength) {
          const boldText = textContent.substring(startPos, textContent.length);
          replaceNodes.push(newBoldElement(boldText));
          replaceNode(nodes[startNodeIndex], replaceNodes);
          remainingBoldLength -= boldText.length;
          replaceNodes = [];
          startPos = 0;
          startNodeIndex += 1;
        } else {
          const boldText = textContent.substring(
            startPos,
            startPos + remainingBoldLength
          );
          replaceNodes.push(newBoldElement(boldText));
          remainingBoldLength = 0;
          startPos += boldText.length;
        }
      }

      while (startNodeIndex !== nodes.length) {
        const textContent = textContents[startNodeIndex];
        if (startNodeIndex < endNodeIndex) {
          const text = textContent.substring(startPos);
          replaceNodes.push(document.createTextNode(text));
          replaceNode(nodes[startNodeIndex], replaceNodes);
          replaceNodes = [];
          startNodeIndex += 1;
          startPos = 0;
        } else {
          const text = textContent.substring(startPos, endPos);
          startPos = endPos + 1;
          endPos = startPos + 1;
          replaceNodes.push(document.createTextNode(text));
          break;
        }
      }
    }
  }

  const cardContainer = document.getElementById("qa");
  forEachChildTextNodes(cardContainer, [], boldNodes);
})();
