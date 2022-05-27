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

  // Ignore node if any of the filters return true
  const excludeFilters = [
    (elem) => elem.tagName === "SCRIPT",
    (elem) => elem.tagName === "STYLE",
    (elem) => elem.classList.contains("cloze"),
  ];

  function newBoldElement(text) {
    const elem = document.createElement("b");
    elem.innerText = text;
    return elem;
  }

  function indexOfWhitespace(text, startPos) {
    const whitespaces = [" ", "\n", "\t"];
    let nextPos = text.length;
    for (const whitespace of whitespaces) {
      const next = text.indexOf(whitespace, startPos);
      if (next !== -1 && next < nextPos) {
        nextPos = next;
      }
    }
    if (nextPos === text.length) {
      nextPos = -1;
    }
    return nextPos;
  }

  // Bolds a line of words
  class BionicReaderBolder {
    constructor(nodes) {
      this.nodes = nodes;
      this.startNodeIndex = 0;
      this.startPos = 0;
      this.replaceNodes = [];
      while (!this.isFinished()) {
        this.runWithinNode();
        this.runInterNode();
      }
    }

    static run(nodes) {
      new BionicReaderBolder(nodes);
    }

    isFinished() {
      return this.startNodeIndex === this.nodes.length;
    }

    replaceNode() {
      const node = this.nodes[this.startNodeIndex];
      const parent = node.parentNode;
      for (let add of this.replaceNodes) {
        parent.insertBefore(add, node);
      }
      parent.removeChild(node);
      this.replaceNodes = [];
    }

    runWithinNode() {
      const textContent = this.nodes[this.startNodeIndex].textContent;
      let nextPos = indexOfWhitespace(textContent, this.startPos);
      while (nextPos !== -1) {
        const word = textContent.substring(this.startPos, nextPos);
        const boldLength = getBoldLength(word);
        this.replaceNodes.push(newBoldElement(word.substring(0, boldLength)));
        this.replaceNodes.push(
          document.createTextNode(
            word.substring(boldLength, nextPos) + textContent[nextPos]
          )
        );
        this.startPos = nextPos + 1;
        nextPos = indexOfWhitespace(textContent, this.startPos);
      }
    }

    // after this, startPos is likely to be at whitespace char
    runInterNode() {
      let word = "";
      let endNodeIndex = this.startNodeIndex;
      let endPos = this.startPos; // last word char pos + 1

      // Find word boundary
      while (endNodeIndex < this.nodes.length) {
        const textContent = this.nodes[endNodeIndex].textContent;
        let nextPos = indexOfWhitespace(textContent, endPos);
        if (nextPos === -1) {
          word += textContent.substring(endPos);
          endNodeIndex += 1;
          endPos = 0;
        } else {
          word += textContent.substring(endPos, nextPos);
          endPos = nextPos;
          break;
        }
      }
      // Calculate bold length
      let remainingBoldLength = getBoldLength(word);

      // Bold part of word
      while (remainingBoldLength > 0) {
        const textContent = this.nodes[this.startNodeIndex].textContent;
        if (remainingBoldLength > textContent.length - this.startPos) {
          const wordPart = textContent.substring(this.startPos);
          remainingBoldLength -= wordPart.length;
          this.replaceNodes.push(newBoldElement(wordPart));
          this.replaceNode();
          this.startNodeIndex += 1;
          this.startPos = 0;
        } else {
          const wordPart = textContent.substring(
            this.startPos,
            this.startPos + remainingBoldLength
          );
          this.startPos += remainingBoldLength;
          this.replaceNodes.push(newBoldElement(wordPart));
          remainingBoldLength -= wordPart.length;
        }
      }

      // Add non-bolded part of words
      while (this.startNodeIndex < endNodeIndex) {
        const textContent = this.nodes[this.startNodeIndex].textContent;
        const wordPart = textContent.substring(this.startPos);
        if (wordPart.length > 0) {
          this.replaceNodes.push(document.createTextNode(wordPart));
        }
        this.replaceNode();
        this.startNodeIndex += 1;
        this.startPos = 0;
      }

      if (this.startPos < endPos) {
        const textContent = this.nodes[this.startNodeIndex].textContent;
        const wordPart = textContent.substring(this.startPos, endPos);
        if (wordPart.length > 0) {
          this.replaceNodes.push(document.createTextNode(wordPart));
        }
        this.startPos = endPos;
      }
    }
  }

  /**
   * Builds a list of (list of nodes that makes up one non-line-broken line)
   * @param {Node} elem
   * @param {Node[][]} - list of list of text nodes. Must not be empty, last element must be a list.
   * @returns {void}
   */
  function forTextNodesInTree(elem, nodes, exclude = false) {
    const children = elem.childNodes;
    for (const filter of excludeFilters) {
      if (filter(elem)) {
        exclude = true;
        break;
      }
    }
    for (const child of children) {
      if (child.nodeType === Node.ELEMENT_NODE) {
        const style = window.getComputedStyle(child);
        if (
          child.tagName !== "BR" &&
          (style === "inline" || style === "inline-block")
        ) {
          forTextNodesInTree(child, nodes, exclude);
        } else {
          if (nodes[nodes.length - 1].length > 0) {
            nodes.push([]);
          }
          forTextNodesInTree(child, nodes, exclude);
        }
      } else if (
        !exclude &&
        child.nodeType === Node.TEXT_NODE &&
        child.textContent.length > 0
      ) {
        nodes[nodes.length - 1].push(child);
      }
    }
  }

  function makeBionic() {
    const cardContainer = document.getElementById("qa");
    cardContainer.normalize();

    let nodesLines = [[]];
    forTextNodesInTree(cardContainer, nodesLines);
    for (const nodes of nodesLines) {
      BionicReaderBolder.run(nodes);
    }

    cardContainer.normalize();
  }

  let start = performance.now();
  makeBionic();
  let end = performance.now();
  console.log(`Initialized bionic reading: ${end - start}ms`);
})();
